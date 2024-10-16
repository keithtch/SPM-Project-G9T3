export function setDateLimits(today) {
    // Calculate two months back
    const minDate = new Date(today);
    minDate.setMonth(today.getMonth() - 2);

    // If minDate is invalid, adjust to the last day of the month
    if (minDate.getDate() !== today.getDate()) {
        // Set to last day of the new month
        minDate.setDate(0); // Set to 0 gets the last day of the previous month
    }

    // Calculate three months forward
    const maxDate = new Date(today);
    maxDate.setMonth(today.getMonth() + 3);

    // If maxDate is invalid, adjust to the last day of the month
    if (maxDate.getDate() !== today.getDate()) {
        // Set to last day of the new month
        maxDate.setDate(0); // Set to 0 gets the last day of the previous month
    }

    // Format the dates to YYYY-MM-DD
    return {
        minDate: minDate.toISOString().split("T")[0],
        maxDate: maxDate.toISOString().split("T")[0],
    };
}
