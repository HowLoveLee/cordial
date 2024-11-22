import { Calendar } from 'vanilla-calendar-pro';
import 'vanilla-calendar-pro/styles/index.css';

const options = {
  firstWeekday: 0,
  selectedWeekends: [0,6],
  selectedTheme: 'dark',
};

const calendar = new Calendar('#calendar', options);
calendar.init();