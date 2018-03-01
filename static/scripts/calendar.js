var monthNames = [
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember"
];

var ALLOWED_MONTHS_AHEAD = 1;
var monthsAhead = 0;

var NUM_WEEKS_PER_PAGE = 6;

var monthLabelElem = document.getElementById("cal-month-label");
var dayElems = new Array(7*NUM_WEEKS_PER_PAGE);

var currentMonth, currentYear, daysFromPrevMonth;

{
    var now = new Date();
    currentMonth = now.getMonth();
    currentYear = now.getFullYear();
}

for (var week = 0; week < NUM_WEEKS_PER_PAGE; week++) {
    for (var day = 0; day < 7; day++) {
        var index = 7 * week + day;
        dayElems[index] = document.getElementById("cal-day-" + index.toString());
    }
}

function Time(timespec) {
    var parts = timespec.split(":");
    
    this.hours = parseInt(parts[0]);
    this.minutes = parseInt(parts[1]);
    
    if (parts.length == 3)
        this.seconds = parseInt(parts[2]);
    else
        this.seconds = 0;
    
}

Time.prototype.toSeconds = function() {
    return this.hours*60*60 + this.minutes*60 + this.seconds;
}

function Availability(time_st, time_end, weekday) {
    this.time_st = time_st;
    this.time_end = time_end;
    this.weekday = weekday;
}

function TimeEvent(time, start_or_end) {
    this.time = time;
    this.start_or_end = start_or_end;
}

function compareTimeEvent(a, b) {
    if (a.time.hours < b.time.hours)
        return -1;
    else if (a.time.hours > b.time.hours)
        return 1;
    
    if (a.time.minutes < b.time.minutes)
        return -1;
    else if (a.time.minutes > b.time.minutes)
        return 1;
    
    if (a.time.seconds < b.time.seconds)
        return -1;
    else if (a.time.seconds > b.time.seconds)
        return 1;
    
    return 0;
}

function resetCalendar() {
    monthLabelElem.innerText = monthNames[currentMonth] + " " + currentYear.toString();

    // On this page of the calendar, how many days from the previous month are visible?
    // And from next month?
    // Let's find out.
    var daysFromNextMonth;

    {
        var firstDayThisMonth = new Date(currentYear, currentMonth, 1);

        // We need to decrement the weekday because the JavaScript standard
        // starts weekdays at Sunday, but in Indonesia they start on Monday.
        daysFromPrevMonth = firstDayThisMonth.getDay() - 1;
        if (daysFromPrevMonth < 0)
            daysFromPrevMonth += 7;

        var lastDayThisMonth = new Date(currentYear, currentMonth, 1);
        for (var i = 2; i <= 31; i++) {
            var candidate = new Date(currentYear, currentMonth, i);
            if (candidate.getMonth() != currentMonth)
                break;
            lastDayThisMonth = candidate;
        }

        daysFromNextMonth = 7 * NUM_WEEKS_PER_PAGE - (daysFromPrevMonth + lastDayThisMonth.getDate());
    }

    for (var week = 0; week < NUM_WEEKS_PER_PAGE; week++) {
        for (var day = 0; day < 7; day++) {
            var index = 7 * week + day;

            if (index < daysFromPrevMonth || index >= 7 * NUM_WEEKS_PER_PAGE - daysFromNextMonth) {
                dayElems[index].innerHTML = "&nbsp;";
                dayElems[index].setAttribute("data-this-month", "false");
            } else {
                var dayNum = (index - daysFromPrevMonth) + 1;
                var html = "<div class=\"cal-day-number\">" + dayNum.toString() + "</div>";

                // We're creating a little stripe that shows availabilities
                var eventArray = []; // Contains time STARTs and time ENDs

                // Add all STARTs and ENDs to an array
                for (var a_i = 0; a_i < availabilities.length; a_i++) {
                    if (availabilities[a_i].weekday == day) {
                        eventArray[eventArray.length] = new TimeEvent(availabilities[a_i].time_st, "start");
                        eventArray[eventArray.length] = new TimeEvent(availabilities[a_i].time_end, "end");
                    }
                }

                // Sort by time
                eventArray.sort(compareTimeEvent);

                // Create the stripe
                var SECONDS_IN_DAY = 24 * 60 * 60;
                var in_avail_slot = false;
                var depth = 0;
                var currentSeconds = 0;
                for (var ev_i = 0; ev_i < eventArray.length; ev_i++) {
                    var event = eventArray[ev_i];

                    if (event.start_or_end == "start")
                        depth++;
                    else
                        depth--;

                    if (in_avail_slot) {
                        if (depth <= 0) {
                            in_avail_slot = false;
                            var s = event.time.toSeconds();
                            var width = 100 * (s - currentSeconds) / SECONDS_IN_DAY;
                            html += "<div class=\"cal-ok-slot\" aria-hidden=\"true\" style=\"width:" + width.toString() + "%;\"></div>";
                            currentSeconds = s;
                        }
                    } else {
                        if (depth > 0) {
                            in_avail_slot = true;
                            var s = event.time.toSeconds();
                            var width = 100 * (s - currentSeconds) / SECONDS_IN_DAY;
                            html += "<div class=\"cal-space-slot\" aria-hidden=\"true\" style=\"width:" + width.toString() + "%;\"></div>";
                            currentSeconds = s;
                        }
                    }
                }

                var leftoverWidth = 100 * (SECONDS_IN_DAY - currentSeconds) / SECONDS_IN_DAY;
                html += "<div class=\"cal-space-slot\" aria-hidden=\"true\" style=\"width:" + leftoverWidth.toString() + "%;\"></div>";

                dayElems[index].innerHTML = html;
                dayElems[index].setAttribute("data-this-month", "true");
            }
        }
    }

    if (monthsAhead == 0) {
        document.getElementById("cal-prev-btn").setAttribute("disabled", "disabled");
    } else {
        document.getElementById("cal-prev-btn").removeAttribute("disabled");
    }

    if (monthsAhead == ALLOWED_MONTHS_AHEAD) {
        document.getElementById("cal-next-btn").setAttribute("disabled", "disabled");
    } else {
        document.getElementById("cal-next-btn").removeAttribute("disabled");
    }
}

function prevMonth() {
    if (monthsAhead > 0) {
        var newMonth = currentMonth - 1;
        if (newMonth < 0) {
            newMonth += 12;
            currentYear--;
        }
        currentMonth = newMonth;
        monthsAhead--;
        resetCalendar();
    }
}

function nextMonth() {
    if (monthsAhead < ALLOWED_MONTHS_AHEAD) {
        var newMonth = currentMonth + 1;
        if (newMonth >= 12) {
            newMonth -= 12;
            currentYear++;
        }
        monthsAhead++;
        currentMonth = newMonth;
        resetCalendar();
    }
}

function viewDay(index) {
    var dayCell = document.getElementById("cal-day-" + index.toString());

    if (dayCell.getAttribute("data-this-month") == "true") {
        var month = currentMonth + 1;
        var day = (index - daysFromPrevMonth) + 1;
        window.location = "/psikolog/" + psyc_id.toString() + "/" + currentYear.toString() + "/" + month.toString() + "/" + day.toString();
    }
}
