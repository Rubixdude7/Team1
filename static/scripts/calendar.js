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

var NUM_WEEKS_PER_PAGE = 6;

var monthLabelElem = document.getElementById("cal-month-label");
var dayElems = new Array(7*NUM_WEEKS_PER_PAGE);

var currentMonth, currentYear;

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

function resetCalendar() {
    monthLabelElem.innerText = monthNames[currentMonth] + " " + currentYear.toString();

    // On this page of the calendar, how many days from the previous month are visible?
    // And from next month?
    // Let's find out.
    var daysFromPrevMonth, daysFromNextMonth;

    {
        var firstDayThisMonth = new Date(currentYear, currentMonth, 1);
        daysFromPrevMonth = firstDayThisMonth.getDay();

        var lastDayThisMonth = new Date(currentYear, currentMonth, 1);
        for (var i = 2; i <= 31; i++) {
            var candidate = new Date(currentYear, currentMonth, i);
            if (candidate.getMonth() != currentMonth)
                break;
            lastDayThisMonth = candidate;
        }

        daysFromNextMonth = 7*NUM_WEEKS_PER_PAGE - (daysFromPrevMonth + lastDayThisMonth.getDate());
    }

    for (var week = 0; week < NUM_WEEKS_PER_PAGE; week++) {
        for (var day = 0; day < 7; day++) {
            var index = 7 * week + day;

            if (index < daysFromPrevMonth || index >= 7*NUM_WEEKS_PER_PAGE - daysFromNextMonth) {
                dayElems[index].innerHTML = "&nbsp;";
                dayElems[index].setAttribute("data-this-month", "false");
            } else {
                var dayNum = (index - daysFromPrevMonth) + 1;
                dayElems[index].innerHTML = "<div class=\"cal-day-number\">" + dayNum.toString() + "</div>";
                dayElems[index].setAttribute("data-this-month", "true");
            }
        }
    }
}

function prevMonth() {
    var newMonth = currentMonth - 1;
    if (newMonth < 0) {
        newMonth += 12;
        currentYear--;
    }
    currentMonth = newMonth;
    resetCalendar();
}

function nextMonth() {
    var newMonth = currentMonth + 1;
    if (newMonth >= 12) {
        newMonth -= 12;
        currentYear++;
    }
    currentMonth = newMonth;
    resetCalendar();
}

resetCalendar();
