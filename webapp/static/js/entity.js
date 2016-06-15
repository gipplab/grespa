var Entity = function (id, cb) {
    var public = this;
    var __co = {};
    var __id;
    var __data;

    function __init() {
        var __id; 
        if (typeof id === 'number') {
            __id = id;  //new data, specified by ID
            $.post('/co/EntityByID/'+__id, {}, 'json').done(function (data) {
                if (!data.error){
                    __data = data.results[0];
                    if (cb) cb(__data);
                }
            });  
        } else {
            return;    
        }

    }
    __init();
}