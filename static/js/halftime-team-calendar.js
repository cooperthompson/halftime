$(function () {
    $('#calendar').fullCalendar({
        header: false,
        defaultView: 'seasonView',
        views: {
            seasonView: {
                type: 'list',
                listDayFormat: 'dddd',
                listDayAltFormat: 'LL',
                visibleRange: function (currentDate) {
                    return {
                        start: currentDate.clone().subtract(8, 'weeks'),
                        end: currentDate.clone().add(8, 'weeks') // exclusive end, so 3
                    };
                }
            }
        }
    })
});
