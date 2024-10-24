export function setDateLimits(today) {
    // Calculate two months back
    const minDate = new Date(today);
    minDate.setMonth(today.getMonth() - 2);

    // If minDate is invalid (e.g., February 30), adjust to the last day of the previous month
    if (minDate.getDate() !== today.getDate()) {
        minDate.setDate(0); // Set to last day of the previous month
    }

    // Calculate three months forward
    const maxDate = new Date(today);
    maxDate.setMonth(today.getMonth() + 3);
    maxDate.setDate(maxDate.getDate() - 1)

    // Format the dates to YYYY-MM-DD
    return {
        minDate: minDate.toISOString().split("T")[0],
        maxDate: maxDate.toISOString().split("T")[0],
    };
}

