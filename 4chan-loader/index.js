const Promise = require('bluebird');
const rp = require('request-promise');
const db = require('nano')('http://localhost:5984/bigmoney');
const sanitizeHtml = require('sanitize-html');
const unescape = require('unescape');
Promise.promisifyAll(db);

const API_CALL_INTERVAL = 2500;

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
      console.log("Pages retrieved: %d", pages.length);
      let originalPosts = pages.reduce((originalPosts, page) => {
        return originalPosts.concat(page.threads)
      }, [])
      return originalPosts;
    })
    .catch((err) => {
      console.log(err);
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
        throw error
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
  console.log("doc exists: %s", docExists)

  if(docExists){
    let curDoc = await db.getAsync(threadId);
    try{
      await db.insertAsync({posts: thread.posts, _rev: curDoc._rev, _id: new String(threadId)})
    } catch (e) {
      console.log("failed to update thread on db")
      console.log(e)
    }
  }else{
    let body = await db.insertAsync({_id: new String(threadId), posts: thread.posts} );
  }
}



//gets called every API_CALL_INTERVAL ms to initiate a fetch of a thread
async function performNextAction() {
  if (threadIdStack.length == 0) {
    let ops = await getThreads();
   
    //Remove dead threads from the threadLastModified map
    let activeThreadIds = ops.map((op) => {
      return op.no
    })

    threadLastModified = Object.keys(threadLastModified).map(threadId => {
      if(!activeThreadIds.includes(threadId)){
        console.log("thread %s is dead", threadId)
        delete activeThreadIds[threadId];
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
    console.log("Fetching thread %d. %d more left in the stack.", threadId, threadIdStack.length);
    fetchThread(threadId);
  }
}

function start() {
  if (nextActionInterval) {
    throw new Error("The miner is already running");
  }
  console.log("Starting miner");
  nextActionInterval = setInterval(performNextAction, API_CALL_INTERVAL);
}

function stop() {
  if (!nextActionInterval) {
    throw new Error("The miner is already stopped");
  }
  console.log("Stopping miner");
  clearInterval(nextActionInterval);

}

start();
