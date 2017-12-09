const Promise = require('bluebird');
const rp = require('request-promise');
const nano = require('nano');
const log = require('pino')();
const sanitizeHtml = require('sanitize-html');
const url = require('url');
const unescape = require('unescape');

const API_CALL_INTERVAL = 2000;

//DB
const COUCH_URL = process.env.COUCH_CONNECTION_STRING || 'http://localhost:5984';
const COUCH_DATABASE = process.env.COUCH_DATABASE || 'bigmoney';
const db = nano(url.resolve(COUCH_URL, COUCH_DATABASE));

Promise.promisifyAll(db);

//contains the id's of the threads to fetch
var threadIdStack = [];

//stores the interval that triggers performNextAction
var nextActionInterval = null;

// key: threadid, value: last_modified unix timestamp
var threadLastModified = {};

async function getThreads() {
  return rp({
      uri: 'https://a.4cdn.org/biz/threads.json',
      headers: {
        'User-Agent': 'big money enterprise'
      },
      json: true // Automatically parses the JSON string in the response
    })
    .then((pages) => {
      let originalPosts = pages.reduce((originalPosts, page) => {
        return originalPosts.concat(page.threads)
      }, [])
      log.info({retrieved_pages: pages.length, posts: originalPosts.length}, "getThreads")
      return originalPosts;
    })
    .catch((err) => {
      log.error(err);
    })
}

function threadHasDocument(threadId){
  return db.headAsync(threadId).then((headers) => {
      return true;
    }, (error) => {
      if (error.statusCode == 404) {
        // the file is not in the db, so dump the entire it
        //return db.insertAsync(thread, threadId);
        return false;
      } else {
        log.error(error)
      }
    })

}

//pulls the thread data and dumps into the couchdb
async function fetchThread(threadId) {
  let thread = await rp({
    uri: 'https://a.4cdn.org/biz/thread/' + threadId + '.json',
    headers: {
      'User-Agent': 'big money enterprise'
    },
    json: true // Automatically parses the JSON string in the response
  });

  //html sanitize comments 
  thread.posts = thread.posts.map((post) => {
    //Remove HTML
    post.com = sanitizeHtml(post.com, {allowedTags: ['br']}) 
    
    //Turn special HTMl entities into characters
    post.com = unescape(post.com)
    
    //replace break tags with spaces
    post.com = post.com.replace(/<br \/>/g, " ");

    //get rid of reply-to lines ( >>1231283 )
    post.com = post.com.replace(/>>\d*/g, "");
    
    return post
  })

  let docExists = await threadHasDocument(threadId);

  if(docExists){
    let curDoc = await db.getAsync(threadId);
    try{
      await db.insertAsync({posts: thread.posts, _rev: curDoc._rev, _id: new String(threadId)})
      log.info({threadId}, "document created")
    } catch (e) {
      log.error(e);
    }
  }else{
    let body = await db.insertAsync({_id: new String(threadId), posts: thread.posts} );
    log.info({threadId}, "document updated")
  }
}



//gets called every API_CALL_INTERVAL ms to initiate a fetch of a thread
async function performNextAction() {
  if (threadIdStack.length == 0) {
    log.info("getting new thread ids")
    let ops = await getThreads();
   
    //Remove dead threads from the threadLastModified map
    let activeThreadIds = ops.map((op) => {
      return op.no
    })
    
    Object.keys(threadLastModified).map(threadId => {
      if(!activeThreadIds.includes(parseInt(threadId))){
        delete threadLastModified[threadId];
      }
    })
    

    //filter out threads with unchanged last_modified  
    ops = ops.filter((op) => {
      let filter = !threadLastModified[op.no] || threadLastModified < op.last_modified;
      if(filter){
        threadLastModified[op.no] = op.last_modified
      }
      return filter;
  });
  
    let threadIds = ops.map((op) => {
      return op.no
    });

    threadIdStack = threadIdStack.concat(threadIds);
  } else {
    let threadId = threadIdStack.pop();
    log.info({threadId}, "triggering fetch")
    fetchThread(threadId);
  }
}

function start() {
  if (nextActionInterval) {
    throw new Error("The miner is already running");
  }
  log.info("miner start");
  nextActionInterval = setInterval(performNextAction, API_CALL_INTERVAL);
}

function stop() {
  if (!nextActionInterval) {
    throw new Error("The miner is already stopped");
  }
  log.info("miner stop")
  clearInterval(nextActionInterval);

}

start();
