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

    // Add WFH events
    events: [
      {
        id: 7,
        title: "WFH (AM) - John Doe (Engineer)",
        start: "2024-09-20T09:00:00",
        end: "2024-09-20T13:00:00",
        description: "Role: Engineer\nWorking from home (9am-1pm)",
        location: "Home",
        reason: "I AM WESLEY",
      },
      {
        id: 8,
        title: "WFH (PM) - John Doe (Engineer)",
        start: "2024-09-21T14:00:00",
        end: "2024-09-21T18:00:00",
        description: "Role: Engineer\nWorking from home (2pm-6pm)",
        location: "Home",
        reason: "I AM WESLEY",
      },
      {
        id: 9,
        title: "WFH (Full day) - John Doe (Engineer)",
        start: "2024-09-22T09:00:00",
        end: "2024-09-22T18:00:00",
        description: "Role: Engineer\nWorking from home (9am-6pm)",
        location: "Home",
        reason: "I AM WESLEY",
      },
      {
        id: 10,
        title: "WFH (Full day) - John Doe (Engineer)",
        start: "2024-09-23T09:00:00",
        end: "2024-09-23T18:00:00",
        description: "Role: Engineer\nWorking from home (9am-6pm)",
        location: "Home",
        reason: "I AM WESLEY",
      },
    ],

    // Show event details on hover
    eventMouseover: function (event, jsEvent) {
      var boxContent = `
              <strong>${event.title}</strong><br>
              <em>${event.description}</em><br>
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
