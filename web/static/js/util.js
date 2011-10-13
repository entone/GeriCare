DateTime = {

    REMOTE_TZ_OFFSET: Date.today().getTimezoneOffset('UTC'),
    
    MONTHS: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
	DAYS: ['Sun','Mon','Tues','Wed','Thur','Fri','Sat'],
	DAYS_SHORT: ['Sn','M','T','W','Th','F','S'],
    
    getDateString : function(date) {
        //date = Site.Util.DateTime.setLocalTimezone(date);
        
		var formatted_date = (date.getMonth() + 1) + '/' + date.getDate() + '/' +
			date.getFullYear();
		
		return formatted_date;
	},
	
	getTimeString : function(date, isShort) {
	    //date = Site.Util.DateTime.setLocalTimezone(date);
	    //date = Date.create(date);
	    
		var hours 	= date.getHours();
		var minutes 	= Site.Util.DateTime._pad(date.getMinutes());
		
		isShort = isShort || false;
		
		var suffix = "AM";
		if (hours >= 12) {
			suffix = "PM";
			hours = hours - 12;
		}
		if (hours === 0) hours = 12;
		
		var formatted_time = hours+(!isShort && minutes != '00' ? ':' + minutes + ' ' : '')+suffix;
		
		return formatted_time;
	},
	
	getTimestamp: function(datePickerID, timePickerID) {
		var date = $('#' + datePickerID).datepicker('getDate');
		var time = $('#' + timePickerID).parseTime();
		
		if (time){
			date.setHours(time.hour);
			date.setMinutes(time.minute);
		}
		if(date){
		    date = Date.create(date);
		}
			return date;
			
	},
	
	isDateEqual: function (d1, d2) {
		return (d1.getMonth() == d2.getMonth() &&
			d1.getDate() == d2.getDate() &&
			d1.getFullYear() == d2.getFullYear());
	},
	
	_meridiem: function(n, caps) {
	    var m = n >= 12 ? 'PM' : 'AM';
	    if (!(caps || true)) {
	        m = m.toLowerCase();
	    }
	    
	    return m;
	},
	
	_pad: function(n) {
	    return n < 10 ? '0' + n : n;
	}
    
};
