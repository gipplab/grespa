var userName = "x",
    userPass = "x",
    dbHost = "x",
    dbPort = 6543,
    dbName = "x",
    ssl = true;



module.exports = {
    getDBAuth: function () {
        return "postgres://" + userName + ":" + userPass + "@" + dbHost + ":" + dbPort + "/" + dbName + "?ssl=" + ssl;
    },



};