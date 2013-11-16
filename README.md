morpheus-web
============

Go to http://54.204.25.111:8000/ and in the data field submit numbers that you
would like to add. Give the algorithm data field this algorithm to run:

var main = function(data) {
    var sum = 0;
    var delay = 0;
    for(var i = 0; i < data.length; ++i) {
        sum += parseInt(data[i]);
    }
    return returnAsyncResult(sum);
}

To take full advantage of our system please use many new lines in between the
numbers.

Link to iOS app: https://github.com/comyarzaheri/morpheus-ios
