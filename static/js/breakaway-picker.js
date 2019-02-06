$(document).ready(function () {
    var form_processor = function (launch_mode) {
        var form = document.getElementById('breakaway-calendar-selecter');
        var option = document.getElementById(form.team.value);

        if (launch_mode === 'webcal') {
            window.top.location = option.getAttribute('data-webcal');
        }
        if (launch_mode === 'google') {
            window.top.location = option.getAttribute('data-google');
        }
        if (launch_mode === 'online') {
            window.top.location = option.getAttribute('data-online');
        }
    };

    document.getElementById('webcal-button').onclick = function () {
        form_processor('webcal');
    };
    document.getElementById('google-button').onclick = function () {
        form_processor('google');
    };
    document.getElementById('online-button').onclick = function () {
        form_processor('online');
    };

    document.getElementById('breakaway-calendar-selecter').onsubmit = function (event) {
        event.preventDefault();
        form_processor('webcal');
    };
});
