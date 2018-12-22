/**
 * Created by cooper on 12/13/2017.
 */


$(function () {

    $('#team-picker').select2({
        width: "100%"
    });

    $('#subscribe-ics').click(function () {
        var queryParams = "?";
        $('#team-picker').select2('data').forEach(function (team) {
            queryParams += 'team_id=' + team.id + "&";
        });
        window.location.href = "/webcal/" + queryParams;
    });
    $('#subscribe-calendar').click(function () {

    });

});