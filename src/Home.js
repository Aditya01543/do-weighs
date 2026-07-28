import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './Home.css';

const API_BASE = process.env.REACT_APP_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:5000');

function Home() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('form1');
  const [itemSearch, setItemSearch] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [selectedItem, setSelectedItem] = useState({ item_code: '', description: '', unit_weight: null });
  const [form1, setForm1] = useState({ itemCode: '', grossWeight: '', palletWeight: '', overrideUnitWeight: '' });
  const [form2, setForm2] = useState({ itemCode: '', grossWeight: '', palletWeight: '', quantity: '' });
  const [result1, setResult1] = useState(null);
  const [result2, setResult2] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
    fetchHistory();
  }, []);

  useEffect(() => {
    if (!itemSearch || itemSearch.length < 2) {
      setSuggestions([]);
      return;
    }
    const delay = setTimeout(() => {
      searchItems(itemSearch);
    }, 250);
    return () => clearTimeout(delay);
  }, [itemSearch]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const searchItems = async (query) => {
    try {
      const response = await axios.get(`${API_BASE}/api/items`, { params: { q: query } });
      setSuggestions(response.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/history`);
      setHistory(response.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const selectItem = async (item_code) => {
    try {
      const response = await axios.get(`${API_BASE}/api/item/${encodeURIComponent(item_code)}`);
      const item = response.data || {};
      setSelectedItem(item);
      setItemSearch(item.item_code || item_code);
      setForm1((prev) => ({ ...prev, itemCode: item.item_code || item_code }));
      setForm2((prev) => ({ ...prev, itemCode: item.item_code || item_code }));
      setSuggestions([]);
      setResult1(null);
      setResult2(null);
      setMessage('');
      setError('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleTab = (tab) => {
    setActiveTab(tab);
    setMessage('');
    setError('');
  };

  const handleForm1Change = (e) => {
    const { name, value } = e.target;
    setForm1((prev) => ({ ...prev, [name]: value }));
    if (name === 'itemCode') {
      setItemSearch(value);
      setSelectedItem({ item_code: value, description: '', unit_weight: null });
    }
  };

  const handleForm2Change = (e) => {
    const { name, value } = e.target;
    setForm2((prev) => ({ ...prev, [name]: value }));
    if (name === 'itemCode') {
      setItemSearch(value);
      setSelectedItem({ item_code: value, description: '', unit_weight: null });
    }
  };

  const handleCalculate1 = async () => {
    setLoading(true);
    setError('');
    setMessage('');
    setResult1(null);

    try {
      const response = await axios.post(
        `${API_BASE}/api/submit`,
        {
          item_code: form1.itemCode,
          total_weight: form1.grossWeight,
          pallet_weight: form1.palletWeight || 0,
          override_unit_weight: form1.overrideUnitWeight || null,
        },
        { headers: getAuthHeaders() }
      );
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setResult1(response.data);
      }
    } catch (err) {
      setError('Calculation failed. Check inputs and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave1 = async () => {
    if (!result1) {
      setError('Calculate first before saving.');
      return;
    }
    setLoading(true);
    setError('');
    setMessage('');

    try {
      await axios.post(
        `${API_BASE}/api/save-record`,
        {
          item_code: form1.itemCode,
          description: selectedItem.description || result1.description,
          master_unit_weight: selectedItem.unit_weight || result1.master_unit_weight,
          manual_unit_weight: form1.overrideUnitWeight || null,
          gross_weight: form1.grossWeight,
          pallet_weight: form1.palletWeight || 0,
          net_weight: result1.net_weight,
          quantity: result1.quantity,
          rounded_quantity: result1.rounded_quantity,
          save_master: Boolean(form1.overrideUnitWeight),
        },
        { headers: getAuthHeaders() }
      );
      setMessage('Record saved successfully.');
      fetchHistory();
    } catch (err) {
      setError('Failed to save record.');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate2 = async () => {
    setLoading(true);
    setError('');
    setMessage('');
    setResult2(null);

    try {
      const response = await axios.post(
        `${API_BASE}/api/submit`,
        {
          item_code: form2.itemCode,
          total_weight: form2.grossWeight,
          pallet_weight: form2.palletWeight || 0,
          quantity: form2.quantity,
        },
        { headers: getAuthHeaders() }
      );
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setResult2(response.data);
      }
    } catch (err) {
      setError('Calculation failed. Check inputs and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSave2 = async () => {
    if (!result2) {
      setError('Calculate first before saving.');
      return;
    }
    setLoading(true);
    setError('');
    setMessage('');

    try {
      await axios.post(
        `${API_BASE}/api/save-record`,
        {
          item_code: form2.itemCode,
          description: selectedItem.description || result2.description,
          master_unit_weight: selectedItem.unit_weight || result2.master_unit_weight,
          manual_unit_weight: result2.unit_weight_used,
          gross_weight: form2.grossWeight,
          pallet_weight: form2.palletWeight || 0,
          net_weight: result2.net_weight,
          quantity: form2.quantity,
          rounded_quantity: result2.rounded_quantity,
          save_master: true,
        },
        { headers: getAuthHeaders() }
      );
      setMessage('Record saved successfully.');
      fetchHistory();
    } catch (err) {
      setError('Failed to save record.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const handleDownload = () => {
    window.open(`${API_BASE}/download`, '_blank');
  };

  const renderSuggestions = () => {
    if (!suggestions.length) return null;
    return (
      <div className="suggestions-box">
        {suggestions.map((item) => (
          <button
            key={item.item_code}
            type="button"
            className="suggestion-item"
            onClick={() => selectItem(item.item_code)}
          >
            <strong>{item.item_code}</strong> {item.description}
          </button>
        ))}
      </div>
    );
  };

  const formatDate = (iso) => new Date(iso).toLocaleString();

  return (
    <div>
      <header className="navbar">
        <h2 className="brand">Forbes Marshall</h2>
        <div className="navbar-right">
          {user && <span className="user-name">Welcome, {user.name || user.email}!</span>}
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <div className="container">
        <div className="tab-switcher">
          <button className={activeTab === 'form1' ? 'tab active' : 'tab'} onClick={() => handleTab('form1')}>Form 1: Component Count</button>
          <button className={activeTab === 'form2' ? 'tab active' : 'tab'} onClick={() => handleTab('form2')}>Form 2: Net Weight Calculator</button>
        </div>

        <div className="form-panel">
          <div className="form-group">
            <label>Item Code</label>
            <input
              type="text"
              name="itemCode"
              value={activeTab === 'form1' ? form1.itemCode : form2.itemCode}
              onChange={activeTab === 'form1' ? handleForm1Change : handleForm2Change}
              onFocus={() => setItemSearch(activeTab === 'form1' ? form1.itemCode : form2.itemCode)}
            />
            {renderSuggestions()}
          </div>

          <div className="details-row">
            <div className="detail-box">
              <label>Description</label>
              <div>{selectedItem.description || 'N/A'}</div>
            </div>
            <div className="detail-box">
              <label>Master Unit Weight</label>
              <div>{selectedItem.unit_weight != null ? selectedItem.unit_weight : '5 (fallback)'}</div>
            </div>
          </div>

          {activeTab === 'form1' ? (
            <>
              <div className="form-group">
                <label>Gross Weight (kg)</label>
                <input type="number" name="grossWeight" value={form1.grossWeight} onChange={handleForm1Change} />
              </div>
              <div className="form-group">
                <label>Pallet Weight (kg)</label>
                <input type="number" name="palletWeight" value={form1.palletWeight} onChange={handleForm1Change} />
              </div>
              <div className="form-group">
                <label>Override Unit Weight (kg)</label>
                <input type="number" name="overrideUnitWeight" value={form1.overrideUnitWeight} onChange={handleForm1Change} />
              </div>
              <div className="button-row">
                <button className="btn" type="button" onClick={handleCalculate1} disabled={loading}>Calculate</button>
                <button className="btn" type="button" onClick={handleSave1} disabled={loading || !result1}>Save Record</button>
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label>Gross Weight (kg)</label>
                <input type="number" name="grossWeight" value={form2.grossWeight} onChange={handleForm2Change} />
              </div>
              <div className="form-group">
                <label>Pallet Weight (kg)</label>
                <input type="number" name="palletWeight" value={form2.palletWeight} onChange={handleForm2Change} />
              </div>
              <div className="form-group">
                <label>Quantity</label>
                <input type="number" name="quantity" value={form2.quantity} onChange={handleForm2Change} />
              </div>
              <div className="button-row">
                <button className="btn" type="button" onClick={handleCalculate2} disabled={loading}>Calculate</button>
                <button className="btn" type="button" onClick={handleSave2} disabled={loading || !result2}>Save Record</button>
              </div>
            </>
          )}

          {message && <div className="success-box">{message}</div>}
          {error && <div className="error-box">{error}</div>}

          {result1 && (
            <div className="result-box">
              <h3>Form 1 Result</h3>
              <p><strong>Net Weight:</strong> {result1.net_weight} kg</p>
              <p><strong>Unit Weight Used:</strong> {result1.unit_weight_used} kg</p>
              <p><strong>Quantity:</strong> {result1.quantity}</p>
              <p><strong>Rounded Quantity:</strong> {result1.rounded_quantity}</p>
            </div>
          )}

          {result2 && (
            <div className="result-box">
              <h3>Form 2 Result</h3>
              <p><strong>Net Weight:</strong> {result2.net_weight} kg</p>
              <p><strong>Calculated Unit Weight:</strong> {result2.unit_weight_used} kg</p>
              <p><strong>Quantity:</strong> {result2.quantity}</p>
              <p><strong>Rounded Quantity:</strong> {result2.rounded_quantity}</p>
            </div>
          )}

          <button className="btn" onClick={handleDownload}>Download Logs CSV</button>
        </div>

        <div className="history-panel">
          <h3>Saved Records</h3>
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Item Code</th>
                  <th>Description</th>
                  <th>Net Weight</th>
                  <th>Quantity</th>
                  <th>Rounded</th>
                  <th>Operator</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id}>
                    <td>{formatDate(item.created_at)}</td>
                    <td>{item.item_code}</td>
                    <td>{item.description}</td>
                    <td>{item.net_weight}</td>
                    <td>{item.quantity}</td>
                    <td>{item.rounded_quantity}</td>
                    <td>{item.scanned_by || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
