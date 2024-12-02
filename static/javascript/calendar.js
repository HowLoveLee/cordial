import { Calendar } from 'vanilla-calendar-pro';
import 'vanilla-calendar-pro/styles/index.css';

// Function to calculate all weekends in the current year
function calculateWeekends() {
  const today = new Date();
  const year = today.getFullYear();
  const weekends = [];

  for (let month = 0; month < 12; month++) {
    const daysInMonth = new Date(year, month + 1, 0).getDate(); // Get number of days in the month

    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dayOfWeek = date.getDay();

      if (dayOfWeek === 0 || dayOfWeek === 6) { // Sunday (0) or Saturday (6)
        weekends.push(formatDate(date));
      }
    }
  }

  return weekends;
}

function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

const weekends = calculateWeekends();
const options = {
  year: false,
  disableDates: weekends,
  selectedTheme: 'light',
  onClickDate(self) {
    const selectedDates = self.context.selectedDates;
    const dateLabel = document.getElementById('date-selected-label');
    const selectedDateInput = document.getElementById('selected-date-input'); // Get the hidden input element

    if (selectedDates.length > 0) {
      const selectedDate = selectedDates[0];
      dateLabel.textContent = selectedDate;
      selectedDateInput.value = selectedDate; // Update the hidden input value
    } else {
      dateLabel.textContent = `None`;
      selectedDateInput.value = ''; // Clear the hidden input value
    }
  },
};

const calendar = new Calendar('#calendar', options);
calendar.init();
