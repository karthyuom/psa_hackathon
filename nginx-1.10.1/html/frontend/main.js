$(function(){
    var test = "testing";
    var live_stream_url = "http://172.20.10.3:5002/video_feed"
    var webSocket = new WebSocket("ws://172.20.10.7:8888");
    webSocket.onopen = wsOnOpen;
    webSocket.onmessage = wsOnMessage;
    webSocket.onclose = wsOnClose;
    webSocket.onerror = wsOnError;

    $("#btn-auto").on("click", autoOnClick.bind(this, webSocket));
    $("#btn-manual").on("click", manualOnClick.bind(this, webSocket));
    $("#btn-ok").on("click", okOnClick.bind(this));

    function wsOnMessage(e){
        console.log("wsOnMessage");
        console.log(JSON.parse(e.data));
        var data = JSON.parse(e.data);
        if(data.type === "ANNOTATED"){
            $("#result").attr("src", data.content);
        } else if(data.type === "ORIGINAL"){
            //$("#original").attr("src", live_stream_url);
        }
        $("#original").attr("src", live_stream_url);
    }

    function wsOnOpen(){
        console.log("wsOnOpen");
        $("#original").attr("src", live_stream_url);
        /*this.send(JSON.stringify({
              "type": "START"
            , "val" : "NULL"
        }));*/
    }

    function wsOnClose(){
        console.log("wsOnClose");
        this.send(JSON.stringify({
              "type": "STOP"
            , "val" : "NULL"
        }));
    }

    function wsOnError(e){
        console.log("wsOnError");
    }

    function autoOnClick(ws, e){
        $("#heading").text("Real Time Video - Auto");
        ws.send(JSON.stringify({
              "type": "AUTO"
            , "val": "NULL"
        }));
    }

    function manualOnClick(ws, e){
        $("#heading").text("Real Time Video - Manual");
        //$("#popup").modal("show");
        ws.send(JSON.stringify({
              "type": "MANUALFACE"
            , "val": "NULL"
        }));
    }

    function okOnClick(e){
        e.preventDefault();
    }
});
