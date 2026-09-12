import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [data, setData] = useState(null);
  const [live, setLive] = useState({
    current_shoppers: 0,
    tracking_ids: [],
  });
  const [status, setStatus] = useState("CONNECTING");

  useEffect(() => {
    const loadData = async () => {
      try {
        const dashboardResponse = await fetch(`${API}/api/dashboard`);
        const liveResponse = await fetch(`${API}/api/live`);

        if (!dashboardResponse.ok || !liveResponse.ok) {
          throw new Error("API unavailable");
        }

        const dashboardData = await dashboardResponse.json();
        const liveData = await liveResponse.json();

        setData(dashboardData);
        setLive(liveData);
        setStatus("ONLINE");
      } catch (error) {
        console.error("API Error:", error);
        setStatus("OFFLINE");
      }
    };

    loadData();

    const interval = setInterval(loadData, 1000);

    return () => clearInterval(interval);
  }, []);

  if (!data) {
    return (
      <div className="loading-screen">
        <div className="loading-logo">RE</div>
        <h1>RetailEdge AI</h1>
        <p>Connecting to Edge Intelligence Engine...</p>
        <div className="loader"></div>
      </div>
    );
  }

  const { shopper, inventory, queue, zones, alerts, store } = data;

  const inventoryHealth =
    inventory.total_products > 0
      ? Math.round(
          (inventory.available / inventory.total_products) * 100
        )
      : 0;

  return (
    <div className="app">

      {/* HEADER */}
      <header className="topbar">

        <div className="brand">
          <div className="brand-icon">RE</div>

          <div>
            <h1>RetailEdge AI</h1>
            <p>Edge Retail Intelligence Platform</p>
          </div>
        </div>

        <div className="top-status">

          <span
            className={`status-dot ${status.toLowerCase()}`}
          ></span>

          <div>
            <strong>AI ENGINE</strong>
            <span>{status}</span>
          </div>

          <div className="store-status">
            <span>●</span>
            {store.name}
          </div>

        </div>

      </header>


      {/* MAIN */}
      <main className="container">

        {/* HERO */}
        <section className="hero">

          <div>

            <div className="eyebrow">
              REAL-TIME OPERATIONS CENTER
            </div>

            <h2>
              Store Intelligence
              <span> Dashboard</span>
            </h2>

            <p>
              Real-time shopper, inventory and queue analytics
              powered by on-device computer vision.
            </p>

          </div>

          <div className="hero-badge">
            <div className="pulse"></div>
            EDGE PROCESSING ACTIVE
          </div>

        </section>


        {/* KPI CARDS */}
        <section className="kpi-grid">

          <div className="kpi-card live-card">

            <div className="kpi-header">
              <span>CURRENT SHOPPERS</span>
              <span className="icon">👥</span>
            </div>

            <div className="kpi-value">
              {live.current_shoppers}
            </div>

            <div className="kpi-footer">
              <span className="live-text">● LIVE</span>
              Anonymous tracking
            </div>

          </div>


          <div className="kpi-card">

            <div className="kpi-header">
              <span>FOOTFALL TODAY</span>
              <span className="icon">🚶</span>
            </div>

            <div className="kpi-value">
              {shopper.entries_today}
            </div>

            <div className="kpi-footer">
              Peak: {shopper.peak} shoppers
            </div>

          </div>


          <div className="kpi-card">

            <div className="kpi-header">
              <span>INVENTORY HEALTH</span>
              <span className="icon">📦</span>
            </div>

            <div className="kpi-value">
              {inventoryHealth}%
            </div>

            <div className="kpi-footer warning-text">
              {inventory.low_stock} low ·{" "}
              {inventory.out_of_stock} OOS
            </div>

          </div>


          <div className="kpi-card">

            <div className="kpi-header">
              <span>CHECKOUT QUEUE</span>
              <span className="icon">🛒</span>
            </div>

            <div className="kpi-value">
              {queue.current}
            </div>

            <div className="kpi-footer">
              Avg wait: {queue.wait_seconds}s
            </div>

          </div>

        </section>


        {/* MAIN DASHBOARD */}
        <section className="main-grid">

          {/* CAMERA */}
          <div className="panel camera-panel">

            <div className="panel-header">

              <div>
                <h3>Live Shopper Monitoring</h3>
                <p>YOLO11 edge inference</p>
              </div>

              <div className="camera-status">
                <span className="pulse"></span>
                CAMERA ACTIVE
              </div>

            </div>


            <div className="camera-view">

              <div className="camera-grid"></div>

              <div className="camera-center">

                <div className="camera-symbol">◉</div>

                <h2>EDGE CAMERA</h2>

                <p>
                  AI vision processing locally
                </p>

                <div className="big-count">
                  {live.current_shoppers}
                </div>

                <span>
                  SHOPPERS DETECTED
                </span>

              </div>


              <div className="camera-overlay top-left">
                LIVE
              </div>

              <div className="camera-overlay top-right">
                YOLO11
              </div>

              <div className="camera-overlay bottom-left">
                TRACKING: {live.tracking_ids?.length || 0}
              </div>

              <div className="camera-overlay bottom-right">
                PRIVACY MODE
              </div>

            </div>

          </div>


          {/* AI INSIGHTS */}
          <div className="panel">

            <div className="panel-header">

              <div>
                <h3>AI Insights</h3>
                <p>
                  Automated operational intelligence
                </p>
              </div>

            </div>


            <div className="insight-list">

              <div className="insight-item success">

                <div className="insight-icon">
                  ✓
                </div>

                <div>
                  <strong>Shopper Detection</strong>

                  <p>
                    {live.current_shoppers} active shopper(s)
                    detected in store
                  </p>
                </div>

              </div>


              <div className="insight-item warning">

                <div className="insight-icon">
                  !
                </div>

                <div>
                  <strong>Inventory Alert</strong>

                  <p>
                    {inventory.low_stock} products require
                    replenishment
                  </p>
                </div>

              </div>


              <div className="insight-item info">

                <div className="insight-icon">
                  ↗
                </div>

                <div>
                  <strong>Queue Intelligence</strong>

                  <p>
                    {queue.current} customers currently waiting
                  </p>
                </div>

              </div>


              <div className="insight-item success">

                <div className="insight-icon">
                  🔒
                </div>

                <div>
                  <strong>Privacy Protected</strong>

                  <p>
                    No facial recognition or PII stored
                  </p>
                </div>

              </div>

            </div>

          </div>

        </section>


        {/* ZONES */}
        <section className="panel zones-panel">

          <div className="panel-header">

            <div>
              <h3>Store Zone Analytics</h3>
              <p>Shopper dwell-time distribution</p>
            </div>

            <span className="analytics-label">
              REAL-TIME
            </span>

          </div>


          <div className="zone-grid">

            {Object.entries(zones).map(
              ([zone, value]) => {

                const max = Math.max(
                  ...Object.values(zones),
                  1
                );

                const percentage = Math.min(
                  (value / max) * 100,
                  100
                );

                return (
                  <div className="zone" key={zone}>

                    <div className="zone-top">
                      <span>{zone}</span>
                      <strong>{value}s</strong>
                    </div>

                    <div className="bar">

                      <div
                        className="bar-fill"
                        style={{
                          width: `${percentage}%`,
                        }}
                      ></div>

                    </div>

                    <small>
                      Dwell time
                    </small>

                  </div>
                );
              }
            )}

          </div>

        </section>


        {/* BOTTOM GRID */}
        <section className="bottom-grid">

          {/* INVENTORY */}
          <div className="panel">

            <div className="panel-header">

              <div>
                <h3>Inventory Status</h3>
                <p>
                  Automated shelf monitoring
                </p>
              </div>

              <span className="inventory-total">
                {inventory.total_products} SKUs
              </span>

            </div>


            <div className="inventory-stats">

              <div className="inventory-stat available">

                <strong>
                  {inventory.available}
                </strong>

                <span>AVAILABLE</span>

              </div>


              <div className="inventory-stat low">

                <strong>
                  {inventory.low_stock}
                </strong>

                <span>LOW STOCK</span>

              </div>


              <div className="inventory-stat out">

                <strong>
                  {inventory.out_of_stock}
                </strong>

                <span>OUT OF STOCK</span>

              </div>

            </div>

          </div>


          {/* QUEUE */}
          <div className="panel">

            <div className="panel-header">

              <div>
                <h3>Queue Intelligence</h3>
                <p>
                  Checkout congestion monitoring
                </p>
              </div>

              <span className="queue-status">
                {queue.status}
              </span>

            </div>


            <div className="queue-content">

              <div className="queue-number">
                {queue.current}
              </div>

              <div>

                <strong>
                  Customers waiting
                </strong>

                <p>
                  Average queue: {queue.average}
                </p>

                <p>
                  Estimated wait: {queue.wait_seconds}s
                </p>

              </div>

            </div>

          </div>

        </section>


        {/* ALERTS */}
        <section className="panel alerts-panel">

          <div className="panel-header">

            <div>
              <h3>Operational Alerts</h3>

              <p>
                AI-generated store notifications
              </p>
            </div>

            <span className="alert-count">
              {alerts.length} ACTIVE
            </span>

          </div>


          <div className="alerts">

            {alerts.map((alert, index) => (

              <div
                className={`alert ${alert.severity}`}
                key={index}
              >

                <div className="alert-symbol">
                  {alert.severity === "warning"
                    ? "!"
                    : "i"}
                </div>

                <div>

                  <strong>
                    {alert.type.toUpperCase()}
                  </strong>

                  <p>
                    {alert.message}
                  </p>

                </div>

              </div>

            ))}

          </div>

        </section>


        {/* FOOTER */}
        <footer>

          <div>
            <strong>RetailEdge AI</strong>

            <span>
              {" "}· Edge Retail Intelligence Platform
            </span>
          </div>

          <div className="footer-right">

            <span>🔒 Privacy First</span>

            <span>⚡ Low Latency</span>

            <span>☁ Cloud Independent</span>

          </div>

        </footer>

      </main>

    </div>
  );
}

export default App;