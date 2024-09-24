$(document).ready(function () {
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

    // Limit view to 2 months back and 3 months ahead
    validRange: {
      start: moment().subtract(2, "months").format("YYYY-MM-DD"),
      end: moment().add(3, "months").format("YYYY-MM-DD"),
    },

    // Events will be dynamically populated by Vue
    events: [],

    // Show event details on hover
    eventMouseover: function (event, jsEvent) {
      var boxContent = `
              <strong>${event.title}</strong><br>
              <em>${event.description}</em><br>
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
