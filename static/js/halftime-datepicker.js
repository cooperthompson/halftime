var context;

$(function () {
   Handlebars.registerHelper("formatDate", function (datetime, format) {
        return moment(datetime).format(format);
    });

    var source = document.getElementById("game-list-template").innerHTML;
    var template = Handlebars.compile(source);
    $(".datepicker").datepicker().change(function () {
        var date = $.datepicker.formatDate('yy-mm-dd', $(".datepicker").datepicker("getDate"));

        $.get('/api/games/?time=' + date, function (data) {
            context = data;
            $('#games').empty().append(template(data));
        })
    }).trigger('change');
});
