import { setDateLimits } from './dateBoundaryUtils.js';

describe('setDateLimits', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should set minDate to 2 months back and maxDate to 3 months forward', () => {
    // Mock today's date to January 15, 2024
    const mockDate = new Date('2024-01-15');
    jest.setSystemTime(mockDate);

    const { minDate, maxDate } = setDateLimits(new Date());

    // Expect minDate to be two months back (e.g., November 15, 2023)
    expect(minDate).toBe('2023-11-15');
    // Expect maxDate to be three months forward (e.g., April 15, 2024)
    expect(maxDate).toBe('2024-04-14');
  });

  it('should consider edge case where month is more than 30days correctly', () => {
    // Mock today's date to March 31, 2024
    const mockDate = new Date('2024-03-31');
    jest.setSystemTime(mockDate);

    const { minDate, maxDate } = setDateLimits(new Date());

    // Expect minDate to be January 31, 2024
    expect(minDate).toBe('2024-01-31');
    // Expect maxDate to be June 30, 2024
    expect(maxDate).toBe('2024-06-30');
  });

  it('should consider another edge case where month is less than 30 days correctly', () => {
    // Mock today's date to April 30, 2024
    const mockDate = new Date('2024-04-30');
    jest.setSystemTime(mockDate);

    const { minDate, maxDate } = setDateLimits(new Date());

    // Expect minDate to be February 29, 2024
    expect(minDate).toBe('2024-02-29');
    // Expect maxDate to be July 30, 2024
    expect(maxDate).toBe('2024-07-29');
  });

  it('should consider non-leap year', () => {
    // Mock today's date to April 30, 2025
    const mockDate = new Date('2025-04-30');
    jest.setSystemTime(mockDate);

    const { minDate, maxDate } = setDateLimits(new Date());

    // Expect minDate to be February 28, 2025
    expect(minDate).toBe('2025-02-28');
    // Expect maxDate to be July 29, 2025
    expect(maxDate).toBe('2025-07-29');
  });

  it('should handle date boundaries correctly', () => {
    const mockDate = new Date('2024-01-15');
    jest.setSystemTime(mockDate);

    const { minDate, maxDate } = setDateLimits(new Date());

    // Dates within the range
    expect(new Date('2023-11-15') >= new Date(minDate)).toBe(true);
    expect(new Date('2024-04-14') <= new Date(maxDate)).toBe(true);

    // Dates outside the range
    expect(new Date('2023-11-14') >= new Date(minDate)).toBe(false);
    expect(new Date('2024-04-15') <= new Date(maxDate)).toBe(false);
  });

  it('test', () => {
    // Mock today's date to April 30, 2025
    const mockDate = new Date('2024-10-23');
    jest.setSystemTime(mockDate);

    const { minDate, maxDate } = setDateLimits(new Date());

    // Expect minDate to be February 28, 2025
    expect(minDate).toBe('2024-08-23');
    // Expect maxDate to be July 29, 2025
    expect(maxDate).toBe('2025-01-22');
  });
});
