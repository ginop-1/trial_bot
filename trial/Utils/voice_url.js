var XMLHttpRequest = require("xhr2");

function escapeRegExp(str) {
  return str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
}

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(escapeRegExp(find), "g"), replace);
}

function getURLsound(msg, lang) {
  var httpreq = new XMLHttpRequest();
  var voicetext = msg;
  voicetext = encodeURIComponent(replaceAll(voicetext, "&", " and "));
  var params = "msg=" + msg + "&lang=" + lang + "&source=ttsmp3";
  httpreq.open("POST", "https://ttsmp3.com/makemp3_new.php", true);
  httpreq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  httpreq.overrideMimeType("application/json");
  httpreq.onreadystatechange = function (e) {
    if (this.readyState == 4 && this.status == 200) {
      try {
        var soundarray = JSON.parse(this.responseText);
        if (soundarray["Error"] != 0) {
          console.log("error");
          return;
        }
        console.log(soundarray["URL"]);
      } catch (err) {
        console.log("error")
      }
    }
  };
  httpreq.send(params);
}

getURLsound(process.argv[2], process.argv[3]);
