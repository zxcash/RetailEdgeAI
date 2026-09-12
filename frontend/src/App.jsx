import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const DEMO_DATA = {
  store: {
    name: "RetailEdge Demo Store",
    status: "ONLINE",
  },
  shopper: {
    current: 12,
    entries_today: 128,
    exits_today: 116,
    peak: 24,
  },
  inventory: {
    total_products: 120,
    available: 113,
    low_stock: 5,
    out_of_stock: 2,
  },
  queue: {
    current: 3,
    average: 2.1,
    wait_seconds: 7.5,
    status: "BUSY",
  },
  zones: {
    Grocery: 42,
    Electronics: 31,
    Pharmacy: 58,
    Checkout: 25,
  },
  alerts: [
    {
      type: "inventory",
      severity: "warning",
      message: "Shelf B is running low on stock",
    },
    {
      type: "queue",
      severity: "info",
      message: "Checkout queue is increasing",
    },
  ],
};

const chartData = [34, 42, 39, 55, 48, 61, 57, 69, 64, 78, 71, 84];

function useCountUp(value, duration = 800) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const target = Number(value) || 0;
    let start = null;

    const animate = (time) => {
      if (!start) start = time;

      const progress = Math.min((time - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);

      setDisplay(target * eased);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration]);

  return display;
}

function MagneticButton({ children, onClick, secondary = false }) {
  const ref = useRef(null);

  const move = (event) => {
    const el = ref.current;
    if (!el) return;

    const rect = el.getBoundingClientRect();

    const x = event.clientX - rect.left - rect.width / 2;
    const y = event.clientY - rect.top - rect.height / 2;

    el.style.transform = `translate(${x * 0.12}px, ${y * 0.12}px)`;
  };

  const leave = () => {
    if (ref.current) {
      ref.current.style.transform = "translate(0, 0)";
    }
  };

  return (
    <button
      ref={ref}
      className={`magnetic ${secondary ? "magnetic-secondary" : ""}`}
      onPointerMove={move}
      onPointerLeave={leave}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function AnimatedNumber({ value, suffix = "", decimals = 0 }) {
  const number = useCountUp(value);

  return (
    <>
      {decimals ? number.toFixed(decimals) : Math.round(number)}
      {suffix}
    </>
  );
}

function Sparkline({ data = chartData }) {
  const [hover, setHover] = useState(null);

  const width = 700;
  const height = 230;
  const padding = 20;

  const max = Math.max(...data);
  const min = Math.min(...data);

  const points = data
    .map((value, index) => {
      const x =
        padding +
        (index / Math.max(data.length - 1, 1)) *
          (width - padding * 2);

      const y =
        height -
        padding -
        ((value - min) / Math.max(max - min, 1)) *
          (height - padding * 2);

      return `${x},${y}`;
    })
    .join(" ");

  return (
    <div className="chart-wrap">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="sparkline"
        preserveAspectRatio="none"
      >
        <defs>
          <linearGradient id="chartFill" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopOpacity="0.18" />
            <stop offset="100%" stopOpacity="0" />
          </linearGradient>
        </defs>

        <polyline
          points={`${padding},${height - padding} ${points} ${
            width - padding
          },${height - padding}`}
          fill="url(#chartFill)"
          stroke="none"
        />

        {[0, 1, 2, 3].map((line) => {
          const y =
            padding + (line / 3) * (height - padding * 2);

          return (
            <line
              key={line}
              x1={padding}
              x2={width - padding}
              y1={y}
              y2={y}
              className="chart-grid"
            />
          );
        })}

        <polyline
          points={points}
          fill="none"
          className="chart-line"
        />

        {data.map((value, index) => {
          const x =
            padding +
            (index / Math.max(data.length - 1, 1)) *
              (width - padding * 2);

          const y =
            height -
            padding -
            ((value - min) / Math.max(max - min, 1)) *
              (height - padding * 2);

          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r={hover === index ? 6 : 3}
              className="chart-point"
              onMouseEnter={() => setHover(index)}
              onMouseLeave={() => setHover(null)}
            />
          );
        })}
      </svg>

      {hover !== null && (
        <div
          className="chart-tooltip"
          style={{
            left: `${(hover / (data.length - 1)) * 100}%`,
          }}
        >
          {data[hover]} shoppers
        </div>
      )}

      <div className="chart-labels">
        <span>09:00</span>
        <span>12:00</span>
        <span>15:00</span>
        <span>18:00</span>
        <span>21:00</span>
      </div>
    </div>
  );
}

function CameraView({ shoppers = 0 }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const streamUrl = `${API}/api/video?t=${Date.now()}`;

  return (
    <div className="camera-view">
      {!loaded && !error && (
        <div className="camera-loading">
          <div className="camera-spinner" />
          <span>Connecting to edge camera...</span>
        </div>
      )}

      {error && (
        <div className="camera-error">
          <div className="camera-error-icon">!</div>
          <strong>Camera stream unavailable</strong>
          <span>Waiting for edge vision...</span>
        </div>
      )}

      <img
        src={streamUrl}
        alt="RetailEdge AI live camera"
        className={`camera-stream ${loaded ? "is-loaded" : ""}`}
        onLoad={() => {
          setLoaded(true);
          setError(false);
        }}
        onError={() => {
          setLoaded(false);
          setError(true);
        }}
      />

      {loaded && (
        <>
          <div className="camera-overlay-top">
            <span className="camera-live-dot" />
            <span>EDGE VISION</span>
          </div>

          <div className="camera-overlay-bottom">
            <div>
              <span className="camera-label">LIVE SHOPPERS</span>
              <strong>{shoppers}</strong>
            </div>

            <div className="camera-ai-status">
              <span>AI</span>
              <span>YOLO11</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function ZoneBars({ zones }) {
  const max = Math.max(...Object.values(zones), 1);

  return (
    <div className="zones">
      {Object.entries(zones).map(([name, value]) => (
        <div className="zone-row" key={name}>
          <div className="zone-top">
            <span>{name}</span>
            <strong>{value}</strong>
          </div>

          <div className="zone-track">
            <div
              className="zone-fill"
              style={{ width: `${(value / max) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function Skeleton() {
  return (
    <div className="skeleton-page">
      <div className="skeleton skeleton-nav" />

      <div className="skeleton-hero">
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-subtitle" />
      </div>

      <div className="skeleton-grid">
        {Array.from({ length: 6 }).map((_, index) => (
          <div className="skeleton skeleton-card" key={index} />
        ))}
      </div>
    </div>
  );
}

function App() {
  const [data, setData] = useState(null);
  const [live, setLive] = useState({
    current_shoppers: 12,
    tracking_ids: [],
  });

  const [theme, setTheme] = useState(
    localStorage.getItem("retail-edge-theme") || "dark"
  );

  const [activeSection, setActiveSection] = useState("overview");
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("retail-edge-theme", theme);
  }, [theme]);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const [dashboardResponse, liveResponse] =
          await Promise.all([
            fetch(`${API}/api/dashboard`),
            fetch(`${API}/api/live`),
          ]);

        if (!dashboardResponse.ok) throw new Error();

        const dashboard = await dashboardResponse.json();

        let liveData = live;

        if (liveResponse.ok) {
          liveData = await liveResponse.json();
        }

        if (mounted) {
          setData(dashboard);
          setLive(liveData);
          setApiOnline(true);
        }
      } catch {
        if (mounted) {
          setData(DEMO_DATA);
          setApiOnline(false);
        }
      }
    };

    load();

    const interval = setInterval(load, 2000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const dashboard = data || DEMO_DATA;

  const currentShoppers =
    apiOnline && live.current_shoppers !== undefined
      ? live.current_shoppers
      : dashboard.shopper.current;

  const inventoryPercent = useMemo(() => {
    return Math.round(
      (dashboard.inventory.available /
        dashboard.inventory.total_products) *
        100
    );
  }, [dashboard]);

  if (!data) {
    return <Skeleton />;
  }

  return (
    <div
      className="app-shell"
      onPointerMove={(event) => {
        document.documentElement.style.setProperty(
          "--mouse-x",
          `${event.clientX}px`
        );

        document.documentElement.style.setProperty(
          "--mouse-y",
          `${event.clientY}px`
        );
      }}
    >
      <header className="topbar">
        <a className="brand" href="#overview">
          <span className="brand-mark">
            <span />
            <span />
            <span />
          </span>

          <span>RetailEdge</span>
          <small>AI</small>
        </a>

        <nav className="nav-links">
          {[
            ["overview", "Overview"],
            ["analytics", "Analytics"],
            ["operations", "Operations"],
            ["alerts", "Alerts"],
          ].map(([id, label]) => (
            <a
              href={`#${id}`}
              key={id}
              className={activeSection === id ? "active" : ""}
              onClick={() => setActiveSection(id)}
            >
              {label}
            </a>
          ))}
        </nav>

        <div className="top-actions">
          <button
            className="theme-toggle"
            onClick={() =>
              setTheme(theme === "dark" ? "light" : "dark")
            }
            aria-label="Toggle theme"
          >
            {theme === "dark" ? "☼" : "☾"}
          </button>

          <div className="connection">
            <span className={apiOnline ? "online-dot" : "offline-dot"} />
            {apiOnline ? "Edge online" : "Demo mode"}
          </div>
        </div>
      </header>

      <main>
        <section className="hero" id="overview">
          <div className="hero-copy">
            <div className="status-line">
              <span className="live-dot" />
              LOCAL AI SYSTEM · {dashboard.store.status}
            </div>

            <h1>
              Store intelligence.
              <br />
              <em>At the edge.</em>
            </h1>

            <p>
              Real-time shopper, inventory and queue intelligence
              running locally — designed for fast decisions and
              minimal cloud dependency.
            </p>

            <div className="hero-actions">
              <MagneticButton
                onClick={() =>
                  document
                    .getElementById("analytics")
                    ?.scrollIntoView({ behavior: "smooth" })
                }
              >
                Explore analytics →
              </MagneticButton>

              <MagneticButton
                secondary
                onClick={() =>
                  document
                    .getElementById("operations")
                    ?.scrollIntoView({ behavior: "smooth" })
                }
              >
                View operations
              </MagneticButton>
            </div>
          </div>

          <div className="hero-metric">
            <span>SHOPPERS NOW</span>

            <strong>
              <AnimatedNumber value={currentShoppers} />
            </strong>

            <div className="metric-trend">
              <span>↑ 12.4%</span>
              <small>vs. previous hour</small>
            </div>
          </div>
        </section>

        <section className="bento" id="analytics">
          <div className="bento-card shoppers-card">
            <div className="card-head">
              <span className="eyebrow">FOOTFALL</span>
              <span className="card-meta">TODAY</span>
            </div>

            <div className="big-number">
              <AnimatedNumber
                value={dashboard.shopper.entries_today}
              />
            </div>

            <p>shopper entries</p>

            <div className="mini-stats">
              <div>
                <strong>
                  <AnimatedNumber value={dashboard.shopper.exits_today} />
                </strong>
                <span>exits</span>
              </div>

              <div>
                <strong>
                  <AnimatedNumber value={dashboard.shopper.peak} />
                </strong>
                <span>peak</span>
              </div>
            </div>
          </div>

          <div className="bento-card camera-card">
            <CameraView shoppers={currentShoppers} />
          </div>

          <div className="bento-card inventory-card">
            <div className="card-head">
              <span className="eyebrow">INVENTORY</span>
              <span className="status-pill good">HEALTHY</span>
            </div>

            <div className="inventory-main">
              <div className="ring">
                <svg viewBox="0 0 120 120">
                  <circle
                    className="ring-bg"
                    cx="60"
                    cy="60"
                    r="48"
                  />

                  <circle
                    className="ring-progress"
                    cx="60"
                    cy="60"
                    r="48"
                    style={{
                      strokeDashoffset:
                        302 - (302 * inventoryPercent) / 100,
                    }}
                  />
                </svg>

                <div>
                  <strong>{inventoryPercent}%</strong>
                  <span>available</span>
                </div>
              </div>

              <div className="inventory-numbers">
                <div>
                  <strong>{dashboard.inventory.available}</strong>
                  <span>Available</span>
                </div>

                <div>
                  <strong>{dashboard.inventory.low_stock}</strong>
                  <span>Low stock</span>
                </div>

                <div>
                  <strong>{dashboard.inventory.out_of_stock}</strong>
                  <span>Out of stock</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bento-card queue-card">
            <div className="card-head">
              <span className="eyebrow">QUEUE</span>
              <span className="status-pill warning">
                {dashboard.queue.status}
              </span>
            </div>

            <div className="queue-number">
              <AnimatedNumber value={dashboard.queue.current} />
              <span>people waiting</span>
            </div>

            <div className="queue-info">
              <div>
                <span>AVG. QUEUE</span>
                <strong>
                  {dashboard.queue.average.toFixed(1)}
                </strong>
              </div>

              <div>
                <span>WAIT TIME</span>
                <strong>
                  {dashboard.queue.wait_seconds.toFixed(1)}s
                </strong>
              </div>
            </div>
          </div>

          <div className="bento-card chart-card">
            <div className="card-head">
              <div>
                <span className="eyebrow">SHOPPER ACTIVITY</span>
                <h3>Traffic throughout the day</h3>
              </div>

              <span className="trend-badge">+18.7%</span>
            </div>

            <Sparkline />
          </div>

          <div className="bento-card zones-card">
            <div className="card-head">
              <div>
                <span className="eyebrow">STORE ZONES</span>
                <h3>Live occupancy</h3>
              </div>
            </div>

            <ZoneBars zones={dashboard.zones} />
          </div>

          <div className="bento-card ai-card">
            <div className="ai-orb">
              <div className="orb-core" />
              <div className="orb-ring ring-one" />
              <div className="orb-ring ring-two" />
              <div className="orb-ring ring-three" />
            </div>

            <div>
              <span className="eyebrow">AI INSIGHT</span>

              <h3>
                Checkout traffic is becoming the dominant
                congestion point.
              </h3>

              <p>
                Edge inference recommends monitoring staffing
                levels during the next 30 minutes.
              </p>
            </div>
          </div>
        </section>

        <section className="operations-section" id="operations">
          <div className="section-heading">
            <div>
              <span className="eyebrow">OPERATIONS</span>
              <h2>Everything happening now.</h2>
            </div>

            <span className="section-note">
              Updated every 2 seconds
            </span>
          </div>

          <div className="operations-grid">
            <div className="operation-item">
              <span className="operation-index">01</span>

              <div>
                <strong>People tracking</strong>
                <p>
                  {currentShoppers} active shopper identities
                  detected by YOLO11.
                </p>
              </div>

              <span className="operation-state">ACTIVE</span>
            </div>

            <div className="operation-item">
              <span className="operation-index">02</span>

              <div>
                <strong>Inventory monitoring</strong>
                <p>
                  {dashboard.inventory.low_stock} shelves require
                  attention.
                </p>
              </div>

              <span className="operation-state warning">
                WATCH
              </span>
            </div>

            <div className="operation-item">
              <span className="operation-index">03</span>

              <div>
                <strong>Queue intelligence</strong>
                <p>
                  Current wait time is{" "}
                  {dashboard.queue.wait_seconds.toFixed(1)} seconds.
                </p>
              </div>

              <span className="operation-state warning">
                BUSY
              </span>
            </div>
          </div>
        </section>

        <section className="alerts-section" id="alerts">
          <div className="section-heading">
            <div>
              <span className="eyebrow">ALERT CENTER</span>
              <h2>Signals worth acting on.</h2>
            </div>
          </div>

          <div className="alerts-list">
            {dashboard.alerts.map((alert, index) => (
              <div className="alert-row" key={`${alert.message}-${index}`}>
                <span
                  className={`alert-icon ${alert.severity}`}
                >
                  {alert.severity === "warning" ? "!" : "i"}
                </span>

                <div>
                  <strong>{alert.message}</strong>
                  <p>
                    {alert.type === "inventory"
                      ? "Inventory intelligence"
                      : "Queue intelligence"}
                  </p>
                </div>

                <span className="alert-time">NOW</span>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <div>
          <strong>RetailEdge AI</strong>
          <span>Private intelligence. Local inference.</span>
        </div>

        <div>
          <span>YOLO11</span>
          <span>·</span>
          <span>FastAPI</span>
          <span>·</span>
          <span>Edge Runtime</span>
        </div>
      </footer>
    </div>
  );
}

export default App;