import React, { useState, useEffect } from 'react';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';
import review_icon from "../assets/reviewicon.png";

const Dealers = () => {
  const [dealersList, setDealersList] = useState([]);
  const [states, setStates] = useState([]);

  const get_dealers = async () => {
    try {
      const res = await fetch("/djangoapp/get_dealers");
      const retobj = await res.json();
      if (retobj.status === 200) {
        const all_dealers = retobj.dealers;
        const uniqueStates = [...new Set(all_dealers.map(dealer => dealer.state))];
        setStates(uniqueStates);
        setDealersList(all_dealers);
      }
    } catch (error) {
      console.error("Error fetching dealers:", error);
    }
  };

  const filterDealers = async (state) => {
    try {
      const res = await fetch(`/djangoapp/get_dealers/${state}`);
      const retobj = await res.json();
      if (retobj.status === 200) {
        setDealersList(retobj.dealers);
      }
    } catch (error) {
      console.error("Error filtering dealers:", error);
    }
  };

  useEffect(() => {
    get_dealers();
  }, []);

  let isLoggedIn = sessionStorage.getItem("username") !== null;

  return (
    <div>
      <Header />
      <table className='table'>
        <thead>
          <tr>
            <th>ID</th>
            <th>Dealer Name</th>
            <th>City</th>
            <th>Address</th>
            <th>Zip</th>
            <th>
              <select name="state" id="state" onChange={(e) => filterDealers(e.target.value)}>
                <option value="" selected disabled hidden>State</option>
                <option value="All">All States</option>
                {states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </th>
            {isLoggedIn && <th>Review Dealer</th>}
          </tr>
        </thead>
        <tbody>
          {dealersList.length > 0 ? (
            dealersList.map(dealer => (
              <tr key={dealer.id}>
                <td>{dealer.id}</td>
                <td><a href={`/dealer/${dealer.id}`}>{dealer.full_name || "N/A"}</a></td>
                <td>{dealer.city}</td>
                <td>{dealer.address}</td>
                <td>{dealer.zip}</td>
                <td>{dealer.state}</td>
                {isLoggedIn && (
                  <td>
                    <a href={`/postreview/${dealer.id}`}>
                      <img src={review_icon} className="review_icon" alt="Post Review"/>
                    </a>
                  </td>
                )}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="7">Loading Dealers...</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default Dealers;
