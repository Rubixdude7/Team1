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
    
    StripGroup.prototype.exclude = function(otherGroup) {
        var keep = [];
        
        for (var i = 0; i < this.strips.length; i++) {
            keep[i] = true;
        }
        
        for (var i = 0; i < this.strips.length; i++) {
            for (var j = 0; j < otherGroup.strips.length; j++) {
                var stripA = this.strips[i];
                var stripB = otherGroup.strips[j];
                
                if (stripA.start < stripB.end && stripA.end > stripB.start) {
                    if (stripA.start >= stripB.start && stripA.end <= stripB.end) {
                        keep[i] = false;
                    } else if (stripA.start <= stripB.start && stripA.end < stripB.end) {
                        stripA.end = stripB.start;
                    } else if (stripA.start < stripB.end && stripA.end >= stripB.end) {
                        stripA.start = stripB.end;
                    } else {
                        this.strips[this.strips.length] = new Strip(stripB.end, stripA.end);
                        keep[keep.length] = true;
                        stripA.end = stripB.start;
                    }
                }
            }
        }
        
        // Discard ones we don't keep
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
    };
    
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
    };
    
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
        for (var i = 0; i < this.avails.length; i++) {
            var a = this.avails[i];

            var a_st = new Date(Date.UTC(a['st']['year'], a['st']['month'], a['st']['day'], a['st']['hour'] - 7, a['st']['minute']));
            var a_end = new Date(Date.UTC(a['end']['year'], a['end']['month'], a['end']['day'], a['end']['hour'] - 7, a['end']['minute']));

            var topleft_time = new Date(Date.UTC(this.year, this.month, 1 - daysFromPrevMonth, -7));

            var strip_start = (a_st - topleft_time) / (24.0*60.0*60.0*1000.0);
            var strip_end = (a_end - topleft_time) / (24.0*60.0*60.0*1000.0);

            stripGroup.add(strip_start, strip_end);
        }
        
        stripGroup.normalize();
        stripGroup.combine();
        stripGroup.splitAtIntervals(1.0);
        
        var cal = this;
        this.elem.find('.cal-day').each(function (index, dayElem) {
            dayElem = $(dayElem);
            
            if (index < daysFromPrevMonth || index >= 7*6 - daysFromNextMonth) {
                dayElem.html("&nbsp;");
                dayElem.attr("data-this-month", "false");
                dayElem.removeAttr("data-day");
                dayElem.removeAttr("data-weekday");
            } else {
                var dayNum = (index - daysFromPrevMonth) + 1;
                var html = "<div class=\"cal-day-number\">" + dayNum.toString() + "</div>";

                var lastEnd = index;
                stripGroup.eachInRange(index, (index+1), function(start, end) {
                    html += "<div class=\"cal-space-slot\" style=\"width: " + ((start - lastEnd)*100) + "%;\"></div>";
                    html += "<div class=\"cal-ok-slot\" style=\"width: " + ((end - start)*100) + "%;\"></div>";
                    
                    lastEnd = end;
                });
                
                html += "<div class=\"cal-space-slot\" style=\"width: " + (((index+1) - lastEnd) * 100) + "%;\"></div>";
                
                dayElem.html(html);
                dayElem.attr("data-this-month", "true");
                dayElem.attr("data-day", cal.year.toString() +  "-" + cal.month.toString() + "-" + dayNum.toString());
                dayElem.attr("data-weekday", (index % 7).toString());
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
