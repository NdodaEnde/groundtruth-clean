import React, { useState, useEffect } from 'react';
import { Save, Loader, CheckCircle, AlertCircle, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';
import './ValidationPanel.css';

const ValidationPanel = ({ docId, chunks, onSaveSuccess }) => {
  const [formData, setFormData] = useState(getDefaultFormData());
  const [isExtracting, setIsExtracting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  const [error, setError] = useState('');
  const [hasExtracted, setHasExtracted] = useState(false); // Track if we've already extracted
  const [currentDocId, setCurrentDocId] = useState(null); // Track which doc we extracted
  const [expandedSections, setExpandedSections] = useState({
    header: true,
    inspection: true,
    wheels: true,
    consumables: true,
    tyres: true,
    signatures: false
  });

  // Extract structured data ONLY when document ID changes (not on every tab switch)
  useEffect(() => {
    // Only extract if:
    // 1. We have a docId
    // 2. AND either we haven't extracted yet OR the document changed
    if (docId && (!hasExtracted || docId !== currentDocId)) {
      extractStructuredData();
      setCurrentDocId(docId);
    }
  }, [docId]);

  // Default form structure matching Pre-Trip Checklist - ALL 21 ITEMS
  function getDefaultFormData() {
    return {
      // Header
      vehicle_reg_no: '',
      drivers_name: '',
      date: '',
      vehicle_mileage: '',
      
      // Inspection items 1-11 (with sub-items indented)
      inspection_items: [
        // 1. BODY WORK
        { item_name: '1. BODY WORK', condition: 'Scratched/Dents', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 2. LICENSE DISK
        { item_name: '2. LICENSE DISK', condition: 'Valid', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 3. WINDOW AND WINDSCREEN
        { item_name: '3. WINDOW AND WINDSCREEN', condition: 'No Cracks', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 4. WIPER BLADES
        { item_name: '4. WIPER BLADES', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 5. NUMBER PLATES
        { item_name: '5. NUMBER PLATES', condition: 'Visible', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 6. DOORS/BONNET/BOOT
        { item_name: '6. DOORS/BONNET/BOOT', condition: 'In Place', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 7. EMERGENCY KIT (with sub-items)
        { item_name: '7. EMERGENCY KIT', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        { item_name: 'WHEEL SPANNER', condition: 'In Place', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'WARNING TRIANGLE', condition: 'In Place', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'JACK', condition: 'In Place', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        // 8. HOOTER
        { item_name: '8. HOOTER', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
        // 9. LIGHTS (with sub-items)
        { item_name: '9. LIGHTS', condition: '', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false, isHeader: true },
        { item_name: 'BRAKE LIGHTS', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'HEAD LIGHTS', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'INDICATORS', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'PARKING LIGHTS', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'REVERSE LIGHTS', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'TAIL LIGHTS', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        // 10. RADIO (with sub-items)
        { item_name: '10. RADIO', condition: '', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false, isHeader: true },
        { item_name: 'TWO WAY', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        { item_name: 'COMMERCIAL', condition: 'Working', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: true },
        // 11. SEAT BELTS
        { item_name: '11. SEAT BELTS', condition: 'Operating', pre_trip_yes: false, pre_trip_no: false, remarks: '', post_trip_yes: false, post_trip_no: false, isSubItem: false },
      ],
      
      // Items 12-14: Wheels
      wheels: [
        { item_name: '12. Wheel Caps', before_value: '', after_value: '', type: 'number' },
        { item_name: '13. MAG Wheels', before_value: '', after_value: '', type: 'number' },
        { item_name: '14. Spare Wheel: Brand', before_value: '', after_value: '', type: 'text' },
      ],
      
      // Items 15-18: Consumable levels
      consumables: [
        { item_name: '15. Amount of Fuel', before_level: '', after_level: '' },
        { item_name: '16. Brake Fluid', before_level: '', after_level: '' },
        { item_name: '17. Engine Oil', before_level: '', after_level: '' },
        { item_name: '18. Water', before_level: '', after_level: '' },
      ],
      
      // Items 19-21: Tyre conditions
      tyres: [
        { position: 'Front L', before_condition: '', before_brand: '', after_condition: '', after_brand: '' },
        { position: 'Front R', before_condition: '', before_brand: '', after_condition: '', after_brand: '' },
        { position: 'Rear L', before_condition: '', before_brand: '', after_condition: '', after_brand: '' },
        { position: 'Rear R', before_condition: '', before_brand: '', after_condition: '', after_brand: '' },
      ],
      
      // Fuel card and signatures
      fuel_card_issued: false,
      keys_issued: false,
      receiver_driver_signature: false,
      receiver_name: '',
      corporate_signature: false,
      dept_representative_name: '',
    };
  }

  const extractStructuredData = async () => {
    setIsExtracting(true);
    setError('');
    setSaveStatus(null);

    try {
      const response = await fetch(`/api/extract?doc_id=${docId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Extraction failed');
      }

      const data = await response.json();
      
      // Map extracted data to form structure
      if (data.extracted_data) {
        const extracted = data.extracted_data;
        const newFormData = { ...getDefaultFormData() };
        
        // Map header fields
        if (extracted.vehicle_header) {
          newFormData.vehicle_reg_no = extracted.vehicle_header.vehicle_reg_no || '';
          newFormData.drivers_name = extracted.vehicle_header.drivers_name || '';
          newFormData.date = extracted.vehicle_header.date || '';
          newFormData.vehicle_mileage = extracted.vehicle_header.vehicle_mileage || '';
        }
        
        // Map inspection items if present
        if (extracted.inspection_items && Array.isArray(extracted.inspection_items)) {
          extracted.inspection_items.forEach((extractedItem) => {
            // Find matching item by name (fuzzy match)
            const idx = newFormData.inspection_items.findIndex(formItem => 
              formItem.item_name.toLowerCase().includes(extractedItem.item_name?.toLowerCase() || '') ||
              extractedItem.item_name?.toLowerCase().includes(formItem.item_name.replace(/^\d+\.\s*/, '').toLowerCase())
            );
            if (idx !== -1) {
              newFormData.inspection_items[idx] = {
                ...newFormData.inspection_items[idx],
                pre_trip_yes: extractedItem.pre_trip_yes || false,
                pre_trip_no: extractedItem.pre_trip_no || false,
                remarks: extractedItem.remarks || '',
                post_trip_yes: extractedItem.post_trip_yes || false,
                post_trip_no: extractedItem.post_trip_no || false,
              };
            }
          });
        }
        
        // Map consumables
        if (extracted.consumable_levels && Array.isArray(extracted.consumable_levels)) {
          extracted.consumable_levels.forEach((item, idx) => {
            if (idx < newFormData.consumables.length) {
              newFormData.consumables[idx] = {
                ...newFormData.consumables[idx],
                before_level: item.before_trip_level || item.before_level || '',
                after_level: item.after_trip_level || item.after_level || ''
              };
            }
          });
        }
        
        // Map tyres
        if (extracted.tyre_conditions && Array.isArray(extracted.tyre_conditions)) {
          extracted.tyre_conditions.forEach((item, idx) => {
            if (idx < newFormData.tyres.length) {
              newFormData.tyres[idx] = {
                ...newFormData.tyres[idx],
                before_condition: item.before_condition || '',
                before_brand: item.before_brand || '',
                after_condition: item.after_condition || '',
                after_brand: item.after_brand || ''
              };
            }
          });
        }
        
        // Map signatures
        if (extracted.signatures) {
          newFormData.receiver_name = extracted.signatures.receiver_name || '';
          newFormData.dept_representative_name = extracted.signatures.dept_representative_name || '';
        }
        
        setFormData(newFormData);
        setHasExtracted(true); // Mark that we've successfully extracted
      }
    } catch (err) {
      console.error('Extraction error:', err);
      setError(err.message);
    } finally {
      setIsExtracting(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setSaveStatus(null);
  };

  const handleInspectionChange = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.inspection_items];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, inspection_items: newItems };
    });
    setSaveStatus(null);
  };

  const handleWheelChange = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.wheels];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, wheels: newItems };
    });
    setSaveStatus(null);
  };

  const handleConsumableChange = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.consumables];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, consumables: newItems };
    });
    setSaveStatus(null);
  };

  const handleTyreChange = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.tyres];
      newItems[index] = { ...newItems[index], [field]: value };
      return { ...prev, tyres: newItems };
    });
    setSaveStatus(null);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    setSaveStatus(null);

    try {
      const response = await fetch(`/api/validate?doc_id=${docId}&validated_by=current_user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Save failed');
      }

      setSaveStatus('success');
      
      if (onSaveSuccess) {
        onSaveSuccess(formData);
      }
    } catch (err) {
      console.error('Save error:', err);
      setError(err.message);
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setHasExtracted(false); // Allow re-extraction
    extractStructuredData();
    setSaveStatus(null);
  };

  if (isExtracting) {
    return (
      <div className="validation-loading">
        <Loader className="spinner" size={32} />
        <p>Extracting structured data...</p>
      </div>
    );
  }

  return (
    <div className="validation-panel">
      {/* Action Buttons */}
      <div className="validation-actions">
        <button 
          className="action-btn reset-btn"
          onClick={handleReset}
          disabled={isSaving}
        >
          <RotateCcw size={16} />
          Re-extract
        </button>
        <button 
          className="action-btn save-btn"
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? (
            <>
              <Loader className="spinner" size={16} />
              Saving...
            </>
          ) : (
            <>
              <Save size={16} />
              Save to Database
            </>
          )}
        </button>
      </div>

      {/* Status Messages */}
      {saveStatus === 'success' && (
        <div className="status-message success">
          <CheckCircle size={16} />
          Data validated and saved successfully!
        </div>
      )}

      {(saveStatus === 'error' || error) && (
        <div className="status-message error">
          <AlertCircle size={16} />
          {error || 'Failed to save data'}
        </div>
      )}

      {/* Form Content */}
      <div className="validation-form">
        
        {/* Header Section */}
        <div className="form-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('header')}
          >
            <h4>🚗 Vehicle & Driver Information</h4>
            {expandedSections.header ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expandedSections.header && (
            <div className="section-content">
              <div className="fields-grid">
                <div className="field-item">
                  <label>Vehicle Reg. No.</label>
                  <input
                    type="text"
                    value={formData.vehicle_reg_no}
                    onChange={(e) => handleInputChange('vehicle_reg_no', e.target.value)}
                    placeholder="e.g., KKJ 770 NW"
                  />
                </div>
                <div className="field-item">
                  <label>Driver's Name</label>
                  <input
                    type="text"
                    value={formData.drivers_name}
                    onChange={(e) => handleInputChange('drivers_name', e.target.value)}
                    placeholder="Full name"
                  />
                </div>
                <div className="field-item">
                  <label>Date</label>
                  <input
                    type="text"
                    value={formData.date}
                    onChange={(e) => handleInputChange('date', e.target.value)}
                    placeholder="DD/MM/YY"
                  />
                </div>
                <div className="field-item">
                  <label>Vehicle Mileage</label>
                  <input
                    type="text"
                    value={formData.vehicle_mileage}
                    onChange={(e) => handleInputChange('vehicle_mileage', e.target.value)}
                    placeholder="e.g., 65564"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Inspection Items Section (1-11) */}
        <div className="form-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('inspection')}
          >
            <h4>📋 Pre-Trip Checklist Items (1-11)</h4>
            {expandedSections.inspection ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expandedSections.inspection && (
            <div className="section-content">
              <div className="inspection-table">
                <div className="inspection-header">
                  <span className="col-item">Item</span>
                  <span className="col-condition">Condition</span>
                  <span className="col-pretrip">Pre-Trip</span>
                  <span className="col-remarks">Remarks</span>
                  <span className="col-posttrip">Post-Trip</span>
                </div>
                {formData.inspection_items.map((item, idx) => (
                  <div 
                    key={idx} 
                    className={`inspection-row ${item.isSubItem ? 'sub-item' : ''} ${item.isHeader ? 'header-item' : ''}`}
                  >
                    <span className="col-item">{item.item_name}</span>
                    <span className="col-condition">{item.condition}</span>
                    {!item.isHeader ? (
                      <>
                        <div className="col-pretrip checkbox-group">
                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={item.pre_trip_yes}
                              onChange={(e) => handleInspectionChange(idx, 'pre_trip_yes', e.target.checked)}
                            />
                            <span className="yes">Y</span>
                          </label>
                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={item.pre_trip_no}
                              onChange={(e) => handleInspectionChange(idx, 'pre_trip_no', e.target.checked)}
                            />
                            <span className="no">N</span>
                          </label>
                        </div>
                        <input
                          className="col-remarks remarks-input"
                          type="text"
                          value={item.remarks}
                          onChange={(e) => handleInspectionChange(idx, 'remarks', e.target.value)}
                          placeholder="Remarks"
                        />
                        <div className="col-posttrip checkbox-group">
                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={item.post_trip_yes}
                              onChange={(e) => handleInspectionChange(idx, 'post_trip_yes', e.target.checked)}
                            />
                            <span className="yes">Y</span>
                          </label>
                          <label className="checkbox-label">
                            <input
                              type="checkbox"
                              checked={item.post_trip_no}
                              onChange={(e) => handleInspectionChange(idx, 'post_trip_no', e.target.checked)}
                            />
                            <span className="no">N</span>
                          </label>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="col-pretrip"></div>
                        <div className="col-remarks"></div>
                        <div className="col-posttrip"></div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Wheels Section (12-14) */}
        <div className="form-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('wheels')}
          >
            <h4>🛞 Wheels (12-14)</h4>
            {expandedSections.wheels ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expandedSections.wheels && (
            <div className="section-content">
              <div className="wheels-table">
                <div className="wheels-header">
                  <span className="col-item">Item</span>
                  <span className="col-before">Before Trip/Driver</span>
                  <span className="col-after">After Trip/Driver Officer</span>
                </div>
                {formData.wheels.map((item, idx) => (
                  <div key={idx} className="wheels-row">
                    <span className="col-item">{item.item_name}</span>
                    {item.type === 'number' ? (
                      <>
                        <div className="col-before wheel-options">
                          {['0', '1', '2', '3', '4'].map((num) => (
                            <label key={num} className="wheel-option">
                              <input
                                type="radio"
                                name={`wheel-before-${idx}`}
                                value={num}
                                checked={item.before_value === num}
                                onChange={(e) => handleWheelChange(idx, 'before_value', e.target.value)}
                              />
                              <span>{num}</span>
                            </label>
                          ))}
                        </div>
                        <div className="col-after wheel-options">
                          {['0', '1', '2', '3', '4'].map((num) => (
                            <label key={num} className="wheel-option">
                              <input
                                type="radio"
                                name={`wheel-after-${idx}`}
                                value={num}
                                checked={item.after_value === num}
                                onChange={(e) => handleWheelChange(idx, 'after_value', e.target.value)}
                              />
                              <span>{num}</span>
                            </label>
                          ))}
                        </div>
                      </>
                    ) : (
                      <>
                        <input
                          className="col-before brand-input"
                          type="text"
                          value={item.before_value}
                          onChange={(e) => handleWheelChange(idx, 'before_value', e.target.value)}
                          placeholder="Brand name"
                        />
                        <input
                          className="col-after brand-input"
                          type="text"
                          value={item.after_value}
                          onChange={(e) => handleWheelChange(idx, 'after_value', e.target.value)}
                          placeholder="Brand name"
                        />
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Consumable Levels Section (15-18) */}
        <div className="form-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('consumables')}
          >
            <h4>⛽ Fluid Levels (15-18)</h4>
            {expandedSections.consumables ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expandedSections.consumables && (
            <div className="section-content">
              <div className="consumables-table">
                <div className="consumables-header">
                  <span className="col-item">Item</span>
                  <span className="col-before">Before Trip</span>
                  <span className="col-after">After Trip</span>
                </div>
                {formData.consumables.map((item, idx) => (
                  <div key={idx} className="consumables-row">
                    <span className="col-item">{item.item_name}</span>
                    <select
                      className="col-before"
                      value={item.before_level}
                      onChange={(e) => handleConsumableChange(idx, 'before_level', e.target.value)}
                    >
                      <option value="">Select</option>
                      <option value="F (Full)">F (Full)</option>
                      <option value="3/4">3/4</option>
                      <option value="1/2">1/2</option>
                      <option value="1/4">1/4</option>
                      <option value="E (Empty)">E (Empty)</option>
                    </select>
                    <select
                      className="col-after"
                      value={item.after_level}
                      onChange={(e) => handleConsumableChange(idx, 'after_level', e.target.value)}
                    >
                      <option value="">Select</option>
                      <option value="F (Full)">F (Full)</option>
                      <option value="3/4">3/4</option>
                      <option value="1/2">1/2</option>
                      <option value="1/4">1/4</option>
                      <option value="E (Empty)">E (Empty)</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Tyres Section (19-21) */}
        <div className="form-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('tyres')}
          >
            <h4>🛞 Tyre Conditions (19-21)</h4>
            {expandedSections.tyres ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expandedSections.tyres && (
            <div className="section-content">
              <p className="section-note">19. 4xTyre: Condition | 20. G-Good/F-Fair/B-Bad | 21. 4xTyre: Brand Name</p>
              <div className="tyres-table">
                <div className="tyres-header">
                  <span className="col-position">Position</span>
                  <span className="col-cond">Before Cond.</span>
                  <span className="col-brand">Before Brand</span>
                  <span className="col-cond">After Cond.</span>
                  <span className="col-brand">After Brand</span>
                </div>
                {formData.tyres.map((tyre, idx) => (
                  <div key={idx} className="tyres-row">
                    <span className="col-position">{tyre.position}</span>
                    <select
                      className="col-cond"
                      value={tyre.before_condition}
                      onChange={(e) => handleTyreChange(idx, 'before_condition', e.target.value)}
                    >
                      <option value="">-</option>
                      <option value="Good">Good</option>
                      <option value="Fair">Fair</option>
                      <option value="Bad">Bad</option>
                    </select>
                    <input
                      className="col-brand"
                      type="text"
                      value={tyre.before_brand}
                      onChange={(e) => handleTyreChange(idx, 'before_brand', e.target.value)}
                      placeholder="Brand"
                    />
                    <select
                      className="col-cond"
                      value={tyre.after_condition}
                      onChange={(e) => handleTyreChange(idx, 'after_condition', e.target.value)}
                    >
                      <option value="">-</option>
                      <option value="Good">Good</option>
                      <option value="Fair">Fair</option>
                      <option value="Bad">Bad</option>
                    </select>
                    <input
                      className="col-brand"
                      type="text"
                      value={tyre.after_brand}
                      onChange={(e) => handleTyreChange(idx, 'after_brand', e.target.value)}
                      placeholder="Brand"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Signatures Section */}
        <div className="form-section">
          <div 
            className="section-header"
            onClick={() => toggleSection('signatures')}
          >
            <h4>✍️ Signatures & Fuel Card</h4>
            {expandedSections.signatures ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </div>
          {expandedSections.signatures && (
            <div className="section-content">
              <div className="fields-grid">
                <div className="field-item checkbox-item">
                  <label className="checkbox-field">
                    <input
                      type="checkbox"
                      checked={formData.fuel_card_issued}
                      onChange={(e) => handleInputChange('fuel_card_issued', e.target.checked)}
                    />
                    Fuel Card Issued
                  </label>
                </div>
                <div className="field-item checkbox-item">
                  <label className="checkbox-field">
                    <input
                      type="checkbox"
                      checked={formData.keys_issued}
                      onChange={(e) => handleInputChange('keys_issued', e.target.checked)}
                    />
                    Keys Issued
                  </label>
                </div>
                <div className="field-item">
                  <label>Name of Receiver</label>
                  <input
                    type="text"
                    value={formData.receiver_name}
                    onChange={(e) => handleInputChange('receiver_name', e.target.value)}
                    placeholder="Receiver name"
                  />
                </div>
                <div className="field-item">
                  <label>Dept Representative Name</label>
                  <input
                    type="text"
                    value={formData.dept_representative_name}
                    onChange={(e) => handleInputChange('dept_representative_name', e.target.value)}
                    placeholder="Representative name"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default ValidationPanel;
