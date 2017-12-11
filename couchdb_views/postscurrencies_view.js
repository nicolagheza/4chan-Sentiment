var currencies = [
  ['xmr', 'monero'],
  ['btc', 'bitcoin'],
  ['xlm', 'lumen'],
  ['ltc', 'litecoin'],
  ['iota', 'miota'],
  ['xrp', 'ripple'],
  ['eth', 'ether'],
  ['buy', 'bought', 'buying'],
  ['sell', 'sold', 'selling'],
  ['pump', 'pumping', 'pumped'],
  ['dump', 'dumping', 'dumped']
]

//regular expression map for every currency 
var crex = currencies.reduce(function(map, currencyKeywords) {
  map[currencyKeywords[0]] = new RegExp(currencyKeywords.map(function(currency){ return "\\b"+currency+"\\b"}).join("|"), "gi");
  return map;
}, {});

function (doc) {
  doc.posts.map(function (post){
    if (!post.com)
      return;
    if (post.com) {
        // time is  [ MM DD YY HH mm SS ]
        // rearrange into [ YY MM DD HH mm SS ] for the key
        var time = post.now.match(/\d\d/g);
        var key = [time[2], time[0], time[1], time[3], time[4], time[5]];
        var currencyDetected = false;
        var value = Object.keys(crex).reduce(function(counts, key) {
            var regexp = crex[key];
            var matches = post.com.match(regexp);
            if (matches) {
                var count = matches.length;
                currencyDetected = true;
            } else {
                var count = 0;
                currencyDetected = false;
            }
            counts[key] = count;
            return counts;
        }, {});
        if (currencyDetected)
          emit(key, {time: post.time, comment: post.com, mentions: value});        
    }
  })
}