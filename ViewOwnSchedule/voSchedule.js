import { setDateLimits } from '../ViewTeamSchedule/dateBoundaryUtils.js';

$(document).ready(function () {
  // Calculate date limits
  const today = new Date();
  const { minDate, maxDate } = setDateLimits(today);
  console.log(minDate);
  console.log(maxDate);

  // Add one day to maxDate coz validRange below removes one day
  const maxDateObj = new Date(maxDate);
  maxDateObj.setDate(maxDateObj.getDate() + 1);
  const updatedMaxDate = maxDateObj.toISOString().split("T")[0];
  console.log(minDate);
  console.log(updatedMaxDate); // Updated max date

  // Initialize the calendar
  $("#calendar").fullCalendar({
    // Calendar options
    header: {
      left: "prev,next today",
      center: "title",
      right: "month,agendaWeek,agendaDay",
    },
    defaultView: "month",
    editable: true,

    // Set the valid date range
    validRange: {
      start: minDate,
      end: updatedMaxDate, 
    },

    // Events will be dynamically populated by Vue
    events: [],

    // Show event details on hover
    eventMouseover: function (event, jsEvent) {
      var boxContent = `
              <strong>${event.title}</strong><br>
              <em>${event.description}</em><br>
              Status: ${event.status}<br>
              Shift: ${event.shift}<br>
              Location: ${event.location}<br>
              Reason: ${event.reason}
          `;

      $("#detailBox")
        .html(boxContent)
        .css({
          display: "block",
          top: jsEvent.pageY + 10,
          left: jsEvent.pageX + 10,
        });
    },

    // Hide the box when the mouse leaves both event and the detail box
    eventMouseout: function () {
      $("#detailBox").hide();
    },
  });

  // Hide the box if the mouse leaves the detail box
  $("#detailBox").on("mouseleave", function () {
    $(this).hide();
  });

  // Keep the box position synced with the mouse movement
  $(document).on("mousemove", function (e) {
    $("#detailBox").css({
      top: e.pageY + 10,
      left: e.pageX + 10,
    });
  });
});
