$(function(){
    var webSocket = new WebSocket();
    webSocket.onopen = this.wsOnOpen.bind(this);
    webSocket.onmessage = this.wsOnMessage.bind(this);
    webSocket.onclose = this.wsOnClose.bind(this);
    webSocket.onerror = this.wsOnError.bind(this);

    $("#btn-auto").on("click", this.autoOnClick.bind(this));
    $("#btn-manual").on("click", this.manualOnClick.bind(this));

    function wsOnMessage(e){
        console.log("wsOnMessage");
    }

    function wsOnOpen(){
        console.log("wsOnOpen");
    }

    function wsOnClose(){
        console.log("wsOnClose");
    }

    function wsOnError(){
        console.log("wsOnError");
    }

    function autoOnClick(e){
        console.log(e);
        console.log(webSocket);
    }

    function manualOnClick(e){
    
    }

});
