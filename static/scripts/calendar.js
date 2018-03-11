// Useful functions for generating strips that show availability times.
var calendarStripModule = (function() {
    var mod = {};
    
    var compareStrips = function(a, b) {
        return a.start - b.start;
    };
    
    var Strip = function(start, end) {
        this.start = start;
        this.end = end;
    };
    
    var StripGroup = function() {
        this.strips = [];
    };
    
    StripGroup.prototype.add = function(start, end) {
        this.strips[this.strips.length] = new Strip(start, end);
    };
    
    StripGroup.prototype.combine = function() {
        // combine() - Combines adjacent and overlapping strips.
        // Loop until we're done.
        var keep = [];
        
        for (var i = 0; i < this.strips.length; i++) {
            keep[i] = true;
        }
        
        for (var i = 0; i < this.strips.length; i++) {
            for (var j = 0; j < this.strips.length; j++) {
                if (i != j && keep[i] && keep[j]) {
                    var stripA = this.strips[i];
                    var stripB = this.strips[j];
                    
                    if (stripA.start <= stripB.end && stripA.end >= stripB.start) {
                        stripA.start = Math.min(stripA.start, stripB.start);
                        stripA.end = Math.max(stripA.end, stripB.end);
                        keep[j] = false;
                    }
                }
            }
        }
        
        var newStrips = [];
        for (var i = 0; i < this.strips.length; i++) {
            if (keep[i]) {
                newStrips[newStrips.length] = this.strips[i];
            }
        }
        
        this.strips = newStrips;
        
        this.normalize();
    };
    
    StripGroup.prototype.splitAtIntervals = function(interval) {
        // splitAtIntervals() - Splits existing strips at intervals.
        var done = false;
        while (!done) {
            done = true;
            
            var stripsToAppend = [];
            
            for (var i = 0; i < this.strips.length; i++) {
                var strip = this.strips[i];
                
                if (Math.floor(strip.start / interval) != Math.floor(strip.end / interval)) {
                    stripsToAppend[stripsToAppend.length] = new Strip((Math.floor(strip.start / interval)+1) * interval,
                                                                      strip.end);
                    done = false;
                }
            }
            
            this.strips = this.strips.concat(stripsToAppend);
        }
        
        this.normalize();
    };
    
    StripGroup.prototype.eachInRange = function(start, end, fn) {
        for (var i = 0; i < this.strips.length; i++) {
            var strip = this.strips[i];
            if (strip.start >= start && strip.end <= end) {
                fn(strip.start, strip.end);
            }
        }
    }
    
    StripGroup.prototype.normalize = function() {
        // Make sure starts are before ends
        for (var i = 0; i < this.strips.length; i++) {
            var strip = this.strips[i];
            if (strip.start > strip.end) {
                var temp = strip.start;
                strip.start = strip.end;
                strip.end = temp;
            }
        }
        
        // Sort
        this.strips.sort(compareStrips);
    }
    
    mod.StripGroup = StripGroup;
    
    return mod;
})();

var calendarModule = (function() {
    var mod = {};
    
    // Indonesian month names
    mod.MONTH_NAMES = [
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
    
    // Calendar object: the main part of this module
    var Calendar = function(elem) {
        this.elem = $(elem);
        this.nextBtn = this.elem.find(".cal-next-btn");
        this.prevBtn = this.elem.find(".cal-prev-btn");
        
        var now = new Date();
        this.month = now.getMonth();
        this.year = now.getFullYear();
        
        this.minMonth = this.month;
        this.minYear = this.year;
        
        var max = new Date(this.year, this.month + 2, 1);
        this.maxMonth = max.getMonth();
        this.maxYear = max.getFullYear();
        
        this.avails = [];
    };
    
    Calendar.prototype.setup = function() {
        var cal = this;
        
        // Set handlers for the "prev month" and "next month" buttons
        this.nextBtn.on("click", function() {
            cal.next();
        });
        
        this.prevBtn.on("click", function() {
            cal.prev();
        });
    };
    
    Calendar.prototype.next = function() {
        var d = new Date(this.year, this.month + 1, 1);
        this.month = d.getMonth();
        this.year = d.getFullYear();
        
        this.refreshButtons();
        
        var cal = this;
        this.elem.find(".cal-month-label").fadeOut(400);
        this.elem.find(".cal-body").slideUp(400, function() {
            cal.refresh();
            cal.elem.find(".cal-month-label").fadeIn(400);
            cal.elem.find(".cal-body").slideDown(400);
        });
    };
    
    Calendar.prototype.prev = function() {
        var d = new Date(this.year, this.month - 1, 1);
        this.month = d.getMonth();
        this.year = d.getFullYear();
        
        this.refreshButtons();
        
        var cal = this;
        this.elem.find(".cal-month-label").fadeOut(400);
        this.elem.find(".cal-body").slideUp(400, function() {
            cal.refresh();
            cal.elem.find(".cal-month-label").fadeIn(400);
            cal.elem.find(".cal-body").slideDown(400);
        });
    };
    
    Calendar.prototype.refresh = function() {
        // Set the month label
        this.elem.find(".cal-month-label").text(mod.MONTH_NAMES[this.month] + " " + this.year);
        
        // On this page of the calendar, how many days from the previous month are visible?
        // And from next month?
        // Let's find out.
        var daysFromPrevMonth, daysFromNextMonth;

        {
            var firstDayThisMonth = new Date(this.year, this.month, 1);

            // We need to decrement the weekday because the JavaScript standard
            // starts the weekday at Sunday, but in Indonesia it starts on Monday.
            daysFromPrevMonth = firstDayThisMonth.getDay() - 1;
            if (daysFromPrevMonth < 0)
                daysFromPrevMonth += 7;

            var lastDayThisMonth = new Date(this.year, this.month + 1, 0);

            daysFromNextMonth = 7*6  - (daysFromPrevMonth + lastDayThisMonth.getDate());
        }

                
        var stripGroup = new calendarStripModule.StripGroup();
        for (var cell = 0; cell < 7*6; cell++) {
            for (var i = 0; i < this.avails.length; i++) {
                if (this.avails[i]["weekday"] == cell % 7) {
                    var time_st = this.avails[i]["time_st"];
                    var time_end = this.avails[i]["time_end"];
                    
                    var start = cell*24*60*60 + time_st["hour"]*60*60 + time_st["minute"]*60 + time_st["second"];
                    var end = cell*24*60*60 + time_end["hour"]*60*60 + time_end["minute"]*60 + time_end["second"];
                    
                    stripGroup.add(start, end);
                }
            }
        }
        
        stripGroup.normalize();
        stripGroup.combine();
        stripGroup.splitAtIntervals(24*60*60);
        
        var cal = this;
        this.elem.find('.cal-day').each(function (index, dayElem) {
            dayElem = $(dayElem);
            
            if (index < daysFromPrevMonth || index >= 7*6 - daysFromNextMonth) {
                dayElem.html("&nbsp;");
                dayElem.attr("data-this-month", "false");
            } else {
                var dayNum = (index - daysFromPrevMonth) + 1;
                var html = "<div class=\"cal-day-number\">" + dayNum.toString() + "</div>";
                
                var lastEnd = index*24*60*60;
                stripGroup.eachInRange(index*24*60*60, (index+1)*24*60*60, function(start, end) {
                    html += "<div class=\"cal-space-slot\" style=\"width: " + ((start - lastEnd) * 100 / (24*60*60)) + "%;\"></div>";
                    html += "<div class=\"cal-ok-slot\" style=\"width: " + ((end - start) * 100 / (24*60*60)) + "%;\"></div>";
                    
                    lastEnd = end;
                });
                
                html += "<div class=\"cal-space-slot\" style=\"width: " + (((index+1)*24*60*60 - lastEnd) * 100 / (24*60*60)) + "%;\"></div>";
                
                dayElem.html(html);
                dayElem.attr("data-this-month", "true");
            }
        });

        this.refreshButtons();
    };
    
    Calendar.prototype.refreshButtons = function() {
        if (this.year == this.minYear && this.month == this.minMonth) {
            this.prevBtn.attr("disabled", "disabled");
        } else {
            this.prevBtn.removeAttr("disabled");
        }
        
        if (this.year == this.maxYear && this.month == this.maxMonth) {
            this.nextBtn.attr("disabled", "disabled");
        } else {
            this.nextBtn.removeAttr("disabled");
        }
    };
    
    Calendar.prototype.setAvailabilities = function(avails) {
        this.avails = avails;
    };
    
    mod.Calendar = Calendar;
    
    return mod;
})();
    
    /*
    Calendar: function() {
    },
    refresh = function(calendar_elem) {
        cal = $(calendar_elem);
        
        // Update month name
        cal.find('.cal-month-name').text(this.MONTH_NAMES[currentMonth] + " " + currentYear.toString());

        
    },
    
    setAvailabilities: function(calendar_elem, avails) {
        
    }
};

// Month names in the Indonesian language
var monthNames = 

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

$(document).ready(function() {
    // Initialize all the calendars on the page
    $('.calendar').each(function(index, element) {
        initCalendar(element);
    });
});
*/
