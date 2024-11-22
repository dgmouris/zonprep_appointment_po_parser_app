import React, { useState } from "react";
import Datepicker from "react-tailwindcss-datepicker";

export default function AppointmentDatePicker({dateValue, setDateValue}) {
  const TODAY = new Date();

  const getDifferenceInDays = () => {
    const oneDay = 24 * 60 * 60 * 1000; // milliseconds in one day
    const differenceInTime = Math.abs(dateValue.startDate - dateValue.endDate); // absolute difference in milliseconds
    return Math.round(differenceInTime / oneDay); // convert to days
  }

  return (
    <>
    <h3 className="block text-sm/6 font-semibold text-gray-900">Pick Date Range for Reports: {`(${getDifferenceInDays()} days)`}</h3>

    <div className="flex rounded-md shadow-sm ring-0 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
      <Datepicker
        useRange={true}
        value={dateValue}
        required={true}
        maxDate={TODAY}
        onChange={newValue => setDateValue(newValue)}
      />
    </div>
    </>
  );
};
