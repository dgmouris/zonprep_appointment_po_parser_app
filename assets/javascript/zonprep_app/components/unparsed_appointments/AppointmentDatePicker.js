import React, { useState } from "react";
import Datepicker from "react-tailwindcss-datepicker";



export default function AppointmentDatePicker({dateValue, setDateValue}) {
  const TODAY = new Date();
  return (
    <>
    <h3 className="text-base font-semibold leading-6 text-gray-900">Pick day</h3>
    <div className="flex rounded-md shadow-sm ring-0 ring-inset ring-gray-300 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-600 sm:max-w-md">
      <Datepicker

        asSingle={true}
        useRange={false}
        value={dateValue}
        required={true}
        maxDate={TODAY}
        onChange={newValue => setDateValue(newValue)}
      />
    </div>
    </>
  );
};
