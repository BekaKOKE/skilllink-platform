import { useMemo, useState, type ReactNode } from 'react';
import { motion } from 'framer-motion';
import { useEffect } from 'react';
import {
  ArrowLeft,
  Bell,
  Calendar,
  CheckCircle2,
  Clock,
  DollarSign,
  Filter,
  Hammer,
  Mail,
  MapPin,
  Paintbrush,
  Phone,
  Search,
  ShieldCheck,
  Sparkles,
  Star,
  Wrench,
  Zap,
  Fan,
  Briefcase,
} from 'lucide-react';

type Role = 'client' | 'specialist';
type Page =
  | 'welcome'
  | 'login'
  | 'signup'
  | 'home'
  | 'listing'
  | 'profile'
  | 'booking'
  | 'tracking'
  | 'confirmation'
  | 'feedback'
  | 'dashboard'
  | 'jobs'
  | 'bookings'
  | 'notifications'
  | 'userProfile';

type Specialist = {
  id: number;
  name: string;
  category: string;
  title: string;
  rating: number;
  reviews: number;
  price: number;
  skills: string[];
  certifications: string[];
  verified: boolean;
  description: string;
  phone: string;
  email: string;
  portfolio: string[];
};

type Booking = {
  id: string;
  specialist: string;
  service: string;
  date: string;
  time: string;
  total: number;
  status: string;
  details: string;
};

const categories = [
  { id: 'plumbing', label: 'Plumbing', icon: Wrench },
  { id: 'electrician', label: 'Electrician', icon: Zap },
  { id: 'cleaning', label: 'Cleaning', icon: Sparkles },
  { id: 'ac', label: 'AC Repair', icon: Fan },
  { id: 'carpentry', label: 'Carpentry', icon: Hammer },
  { id: 'painting', label: 'Painting', icon: Paintbrush },
];


const specialistsSeed: Specialist[] = [
  {
    id: 1,
    name: 'Daniel Carter',
    category: 'electrician',
    title: 'Certified Electrician',
    rating: 4.8,
    reviews: 124,
    price: 25,
    skills: ['Wiring', 'Lighting', 'Circuit Repair'],
    certifications: ['Licensed Technician', 'Safety Certified'],
    verified: true,
    description: 'Fast and reliable home electrical repair and installation.',
    phone: '+1 555 102 900',
    email: 'daniel@skilllink.app',
    portfolio: ['Kitchen wiring', 'Smart light setup', 'Fuse box repair'],
  },
  {
    id: 2,
    name: 'Sophia Bennett',
    category: 'cleaning',
    title: 'Home Cleaning Specialist',
    rating: 4.9,
    reviews: 203,
    price: 18,
    skills: ['Deep Cleaning', 'Office Cleaning', 'Move-out Cleaning'],
    certifications: ['Verified Professional'],
    verified: true,
    description: 'Detailed home and office cleaning with eco-friendly products.',
    phone: '+1 555 220 414',
    email: 'sophia@skilllink.app',
    portfolio: ['Apartment deep clean', 'Office refresh', 'Kitchen sanitizing'],
  },
  {
    id: 3,
    name: 'Michael Torres',
    category: 'plumbing',
    title: 'Expert Plumber',
    rating: 4.7,
    reviews: 89,
    price: 22,
    skills: ['Leak Repair', 'Pipe Installation', 'Bathroom Fixtures'],
    certifications: ['Licensed Plumber'],
    verified: true,
    description: 'Affordable plumbing services for homes and small businesses.',
    phone: '+1 555 830 771',
    email: 'michael@skilllink.app',
    portfolio: ['Leak fix', 'Sink installation', 'Bathroom piping'],
  },
  {
    id: 4,
    name: 'Olivia Reed',
    category: 'painting',
    title: 'Interior Painter',
    rating: 4.6,
    reviews: 64,
    price: 20,
    skills: ['Interior Walls', 'Color Matching', 'Touch-ups'],
    certifications: ['Verified Professional'],
    verified: true,
    description: 'Modern paint finishes for homes, bedrooms, and workspaces.',
    phone: '+1 555 743 101',
    email: 'olivia@skilllink.app',
    portfolio: ['Living room refresh', 'Office repaint', 'Accent wall design'],
  },
  {
    id: 5,
    name: 'Ethan Walker',
    category: 'ac',
    title: 'AC Repair Technician',
    rating: 4.8,
    reviews: 111,
    price: 28,
    skills: ['AC Diagnostics', 'Cooling Repair', 'Maintenance'],
    certifications: ['HVAC Certified'],
    verified: true,
    description: 'Efficient AC repair and preventive maintenance for any season.',
    phone: '+1 555 402 988',
    email: 'ethan@skilllink.app',
    portfolio: ['AC tune-up', 'Cooling unit repair', 'Filter replacement'],
  },
  {
    id: 6,
    name: 'Noah Foster',
    category: 'carpentry',
    title: 'Custom Carpenter',
    rating: 4.7,
    reviews: 73,
    price: 27,
    skills: ['Cabinet Repair', 'Woodwork', 'Furniture Assembly'],
    certifications: ['Workshop Certified'],
    verified: true,
    description: 'Precise woodworking and furniture repair with clean finishing.',
    phone: '+1 555 321 665',
    email: 'noah@skilllink.app',
    portfolio: ['Shelf installation', 'Door repair', 'Custom cabinet fit'],
  },
];

const initialReviews = [
  { id: 1, name: 'Emma', rating: 5, text: 'Excellent work, very professional and arrived on time.' },
  { id: 2, name: 'Liam', rating: 4, text: 'Good communication and quality service. Would hire again.' },
];

const initialSpecialistJobs = [
  { id: 'JOB-301', client: 'Alex Johnson', service: 'Electrical Repair', date: '2026-04-08', time: '14:00', status: 'Accepted' },
  { id: 'JOB-302', client: 'Mia Clark', service: 'Lighting Installation', date: '2026-04-09', time: '10:30', status: 'In Progress' },
];

const pageTitles: Record<Page, string> = {
  welcome: 'Welcome',
  login: 'Login',
  signup: 'Sign Up',
  home: 'Home',
  listing: 'Specialists',
  profile: 'Profile',
  booking: 'Booking',
  tracking: 'Order Tracking',
  confirmation: 'Booking Confirmation',
  feedback: 'Review',
  dashboard: 'Dashboard',
  jobs: 'Jobs',
  bookings: 'My Bookings',
  notifications: 'Notifications',
  userProfile: 'My Profile',
};

function IconBadge({ children }: { children: ReactNode }) {
  return <div className="icon-badge">{children}</div>;
}

function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`card ${className}`.trim()}>{children}</div>;
}

function Button({
  children,
  variant = 'primary',
  onClick,
  className = '',
  type = 'button',
}: {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit';
}) {
  return (
    <button type={type} className={`btn btn-${variant} ${className}`.trim()} onClick={onClick}>
      {children}
    </button>
  );
}

function InputField(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={`input ${props.className ?? ''}`.trim()} />;
}

function TextArea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={`textarea ${props.className ?? ''}`.trim()} />;
}

function Badge({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'success' | 'soft' }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

function Avatar({ name }: { name: string }) {
  const initials = name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2);
  return <div className="avatar">{initials}</div>;
}

function Stars({ value }: { value: number }) {
  return (
    <div className="stars">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star key={i} size={16} className={i < Math.round(value) ? 'star active' : 'star'} />
      ))}
    </div>
  );
}

function SectionHeader({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <div className="section-header">
      <h2>{title}</h2>
      {action}
    </div>
  );
}

function StepTracker({ status }: { status: string }) {
  const steps = ['Pending', 'Accepted', 'In Progress', 'Completed'];
  const currentIndex = steps.indexOf(status);
  return (
    <div className="steps-grid">
      {steps.map((step, index) => {
        const done = index < currentIndex;
        const active = index === currentIndex;
        return (
          <div key={step} className="step-item">
            <div className={`step-circle ${done ? 'done' : active ? 'active' : ''}`}>
              {done ? <CheckCircle2 size={18} /> : index + 1}
            </div>
            <span>{step}</span>
          </div>
        );
      })}
    </div>
  );
}

function BottomNav({ role, active, onNavigate }: { role: Role; active: string; onNavigate: (target: string) => void }) {
  const items = role === 'client' ? ['home', 'bookings', 'notifications', 'profile'] : ['home', 'jobs', 'notifications', 'dashboard'];
  return (
    <div className="bottom-nav-wrap">
      <div className="bottom-nav">
        {items.map((item) => (
          <button key={item} className={`bottom-nav-item ${active === item ? 'active' : ''}`} onClick={() => onNavigate(item)}>
            {item === 'notifications' ? (
            <span className="nav-badge-wrap">
              {item}
            </span>
            ) : (
              item
            )}
          </button>
        ))}
      </div>
    </div>
  );
}


export default function App() {
  const [page, setPage] = useState<Page>('welcome');
  const [role, setRole] = useState<Role>('client');
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('rating');
  const [selectedSpecialistId, setSelectedSpecialistId] = useState<number>(1);
  const [bookingDate, setBookingDate] = useState('0000-00-00');
  useEffect(() => {
  const minTime = getMinTime();

  if (bookingTime < minTime) {
    setBookingTime(minTime);
  }
}, [bookingDate]);
  const [bookingTime, setBookingTime] = useState('00:00');
  const getMinTime = () => {
  const today = new Date().toISOString().split('T')[0];

  if (bookingDate === today) {
    const now = new Date();
    return now.toTimeString().slice(0, 5); // HH:MM
  }

  return "00:00";
};
  const [serviceDetails, setServiceDetails] = useState('I need help with a power outlet and living room lights.');
  const [bookingStatus, setBookingStatus] = useState('Pending');
  const [reviews, setReviews] = useState(initialReviews);
  const [notifications, setNotifications] = useState([
  { id: 1, text: 'Welcome to SkillLink!' }]);
  const [unreadCount, setUnreadCount] = useState(1);
  useEffect(() => {
    if (page === 'notifications') {
      setUnreadCount(0);
    }
  }, [page]);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('Very professional and quick service.');
  const [bookings, setBookings] = useState<Booking[]>([]);

  const selectedSpecialist = specialistsSeed.find((s) => s.id === selectedSpecialistId) ?? specialistsSeed[0];

  const filteredSpecialists = useMemo(() => {
    const q = search.toLowerCase();
    const result = specialistsSeed.filter((s) => {
      const matchesCategory = selectedCategory === 'all' || s.category === selectedCategory;
      const matchesSearch =
        s.name.toLowerCase().includes(q) ||
        s.title.toLowerCase().includes(q) ||
        s.skills.join(' ').toLowerCase().includes(q) ||
        s.category.toLowerCase().includes(q);
      return matchesCategory && matchesSearch;
    });

    return [...result].sort((a, b) => {
      if (sortBy === 'price') return a.price - b.price;
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      return b.rating - a.rating;
    });
  }, [search, selectedCategory, sortBy]);

  const goHomeForRole = () => setPage(role === 'client' ? 'home' : 'dashboard');

  const handleBookingConfirm = () => {
    const newBooking: Booking = {
      id: `SKL-${1000 + bookings.length + 1}`,
      specialist: selectedSpecialist.name,
      service: selectedSpecialist.title,
      date: bookingDate,
      time: bookingTime,
      total: selectedSpecialist.price + 3,
      status: 'Pending',
      details: serviceDetails,
    };
    setBookings((prev) => [newBooking, ...prev]);
    setBookingStatus('Pending');
    setPage('confirmation');
    setNotifications((prev) => [
  {
    id: prev.length + 1,
    text: `Booking confirmed with ${selectedSpecialist.name}`
  },
  ...prev
]);
    setUnreadCount((prev) => prev + 1);
  };

  const advanceStatus = () => {
    const statuses = ['Pending', 'Accepted', 'In Progress', 'Completed'];
    const idx = statuses.indexOf(bookingStatus);
    setBookingStatus(statuses[Math.min(idx + 1, statuses.length - 1)]);
  };

  const submitReview = () => {
    setReviews((prev) => [{ id: prev.length + 1, name: 'You', rating: reviewRating, text: reviewComment }, ...prev]);
    setReviewComment('');
    setReviewRating(5);
    setPage('home');
  };

  const topBar = !['welcome', 'login', 'signup'].includes(page) && (
    <div className="topbar">
      <div className="container topbar-inner">
        <div className="topbar-left">
          {!['home', 'dashboard', 'bookings', 'notifications', 'jobs', 'userProfile'].includes(page) && (
            <Button variant="secondary" className="icon-btn" onClick={goHomeForRole}>
              <ArrowLeft size={18} />
            </Button>
          )}
          <div>
            <h1>{pageTitles[page]}</h1>
            <p>SkillLink service marketplace</p>
          </div>
        </div>
          <div className="topbar-right">
            <button
              className="notif-btn"
              onClick={() => {
                setPage('notifications');
                setUnreadCount(0);
              }}
            >
              <Bell size={18} />
              {unreadCount > 0 && (
                <span className="notif-dot">{unreadCount}</span>)}
            </button>

            <div
              onClick={() => {
                setPage('userProfile');
              }}
              style={{ cursor: 'pointer' }}
            >
              <Avatar name={role === 'client' ? 'Client User' : 'Specialist User'} />
            </div>
          </div>
      </div>
    </div>
  );

  return (
    <div className="app-shell">
      {topBar}

      <main className="container page-content">
        {page === 'welcome' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="hero-grid">
            <div className="hero-copy">
              <Badge tone="soft">Service Marketplace</Badge>
              <div>
                <h1 className="hero-title">SkillLink</h1>
                <p className="hero-subtitle">Find trusted service professionals for every job.</p>
                <p className="hero-description">
                  Book verified electricians, plumbers, cleaners, carpenters, painters, and repair specialists through one modern web platform.
                </p>
              </div>
              <div className="button-row">
                <Button onClick={() => setPage('login')}>Log In</Button>
                <Button variant="secondary" onClick={() => setPage('signup')}>Sign Up</Button>
              </div>
            </div>

            <Card className="hero-panel">
              <div className="feature-grid">
                {categories.map((cat) => {
                  const Icon = cat.icon;
                  return (
                    <div key={cat.id} className="mini-card">
                      <IconBadge>
                        <Icon size={22} />
                      </IconBadge>
                      <h3>{cat.label}</h3>
                      <p>Verified specialists and fast booking flow.</p>
                    </div>
                  );
                })}
              </div>
            </Card>
          </motion.div>
        )}

        {page === 'login' && (
          <div className="centered-page">
            <Card className="auth-card">
              <h2>Welcome Back</h2>
              <p className="muted">Log in to continue using SkillLink</p>
              <div className="stack gap-16">
                <InputField placeholder="Email Address" />
                <InputField type="password" placeholder="Password" />
              </div>
              <div className="between-row">
                <button className="link-btn">Forgot Password?</button>
                <select className="select" value={role} onChange={(e) => setRole(e.target.value as Role)}>
                  <option value="client">Client</option>
                  <option value="specialist">Specialist</option>
                </select>
              </div>
              <Button className="full-width" onClick={goHomeForRole}>Log In</Button>
              <p className="center-text muted">Don’t have an account? <button className="link-btn" onClick={() => setPage('signup')}>Sign Up</button></p>
            </Card>
          </div>
        )}

        {page === 'signup' && (
          <div className="centered-page">
            <Card className="auth-card">
              <h2>Create Account</h2>
              <p className="muted">Join SkillLink as a client or service specialist</p>
              <div className="stack gap-16">
                <InputField placeholder="Full Name" />
                <InputField placeholder="Email Address" />
                <InputField placeholder="Phone Number" />
                <InputField type="password" placeholder="Password" />
                <select className="select" value={role} onChange={(e) => setRole(e.target.value as Role)}>
                  <option value="client">Client</option>
                  <option value="specialist">Specialist</option>
                </select>
              </div>
              <Button className="full-width" onClick={goHomeForRole}>Register</Button>
              <p className="center-text muted">Already have an account? <button className="link-btn" onClick={() => setPage('login')}>Log In</button></p>
            </Card>
          </div>
        )}

        {page === 'home' && (
          <div className="stack gap-32">
            <section className="banner">
              <div>
                <p className="banner-eyebrow">Hello, Alex</p>
                <h2>What service do you need today?</h2>
                <p className="banner-text">Search trusted specialists and book in a few clicks.</p>
              </div>
              <div className="searchbar large-search">
                <Search size={18} />
                <input
                  value={search}
                  onChange={(e) => {
                    setSearch(e.target.value);
                    setPage('listing'); // 💥 сразу переходим к результатам
                  }}
                  placeholder="Search for services or specialists"
                />
                <Button
                    variant="secondary"
                    className="small-btn"
                    onClick={() => setPage('listing')}
                >
                  <Search size={16} /> Search
                </Button>
              </div>
            </section>

            <section>
              <SectionHeader title="Service Categories" />
              <div className="cards-grid three-cols">
                {categories.map((cat) => {
                  const Icon = cat.icon;
                  return (
                    <motion.button whileHover={{ y: -3 }} key={cat.id} className="category-card" onClick={() => { setSelectedCategory(cat.id); setPage('listing'); }}>
                      <IconBadge><Icon size={24} /></IconBadge>
                      <h3>{cat.label}</h3>
                      <p>Browse trusted professionals and compare ratings, skills, and prices.</p>
                    </motion.button>
                  );
                })}
              </div>
            </section>

            <section>
              <SectionHeader title="Featured Specialists" action={<Button variant="secondary" onClick={() => setPage('listing')}>View All</Button>} />
              <div className="cards-grid three-cols">
                {specialistsSeed.map((sp) => (
                  <Card key={sp.id}>
                    <div className="specialist-head">
                      <div className="inline-user">
                        <Avatar name={sp.name} />
                        <div>
                          <div className="name-row">
                            <h3>{sp.name}</h3>
                            {sp.verified && <ShieldCheck size={16} className="blue-icon" />}
                          </div>
                          <p className="muted small-text">{sp.title}</p>
                        </div>
                      </div>
                      <Badge tone="soft">From ${sp.price}</Badge>
                    </div>
                    <div className="rating-row"><Stars value={sp.rating} /><span>{sp.rating}</span><span className="muted">({sp.reviews} reviews)</span></div>
                    <div className="tag-row">{sp.skills.slice(0, 3).map((skill) => <Badge key={skill}>{skill}</Badge>)}</div>
                    <div className="button-row stretch-row">
                      <Button variant="secondary" className="flex-1" onClick={() => { setSelectedSpecialistId(sp.id); setPage('profile'); }}>View Profile</Button>
                      <Button className="flex-1" onClick={() => { setSelectedSpecialistId(sp.id); setPage('booking'); }}>Hire</Button>
                    </div>
                  </Card>
                ))}
              </div>
            </section>
          </div>
        )}

        {page === 'listing' && (
          <div className="stack gap-24">
            <div className="toolbar">
              <div className="searchbar">
                <Search size={18} />
                <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search specialists" />
              </div>
              <div className="filters-row">
                <select className="select" value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
                  <option value="all">All Categories</option>
                  {categories.map((cat) => <option key={cat.id} value={cat.id}>{cat.label}</option>)}
                </select>
                <select className="select" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  <option value="rating">Highest Rated</option>
                  <option value="price">Lowest Price</option>
                  <option value="name">Name</option>
                </select>
              </div>
            </div>
            <div className="cards-grid two-cols">
              {filteredSpecialists.map((sp) => (
                <Card key={sp.id}>
                  <div className="listing-card">
                    <div className="listing-main">
                      <Avatar name={sp.name} />
                      <div>
                        <div className="name-row">
                          <h3>{sp.name}</h3>
                          {sp.verified && <ShieldCheck size={16} className="blue-icon" />}
                        </div>
                        <p className="muted">{sp.title}</p>
                        <div className="rating-row"><Stars value={sp.rating} /><span>{sp.rating}</span><span className="muted">({sp.reviews} reviews)</span></div>
                        <div className="tag-row">{sp.skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}</div>
                        <p className="muted small-text mt-12">{sp.description}</p>
                      </div>
                    </div>
                    <div className="listing-actions">
                      <Badge tone="soft">From ${sp.price}</Badge>
                      <Button variant="secondary" onClick={() => { setSelectedSpecialistId(sp.id); setPage('profile'); }}>View Profile</Button>
                      <Button onClick={() => { setSelectedSpecialistId(sp.id); setPage('booking'); }}>Hire</Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {page === 'profile' && (
          <div className="profile-grid">
            <Card>
              <div className="profile-top">
                <Avatar name={selectedSpecialist.name} />
                <div className="profile-main">
                  <div className="name-row">
                    <h2>{selectedSpecialist.name}</h2>
                    {selectedSpecialist.verified && <Badge tone="soft">Verified</Badge>}
                  </div>
                  <p className="profile-role">{selectedSpecialist.title}</p>
                  <div className="rating-row"><Stars value={selectedSpecialist.rating} /><span>{selectedSpecialist.rating} ({selectedSpecialist.reviews} reviews)</span></div>
                  <div className="tag-row">{selectedSpecialist.skills.map((skill) => <Badge key={skill}>{skill}</Badge>)}</div>
                  <p className="muted mt-12">{selectedSpecialist.description}</p>
                  <div className="contact-grid">
                    <div className="contact-item"><Phone size={18} className="blue-icon" /> <span>{selectedSpecialist.phone}</span></div>
                    <div className="contact-item"><Mail size={18} className="blue-icon" /> <span>{selectedSpecialist.email}</span></div>
                  </div>
                </div>
                <Card className="price-card">
                  <p className="muted">Starting from</p>
                  <h2 className="price-hero">${selectedSpecialist.price}</h2>
                  <Button className="full-width" onClick={() => setPage('booking')}>Book Service</Button>
                </Card>
              </div>
            </Card>

            <div className="side-stack">
              <Card>
                <h3>Certifications</h3>
                <div className="tag-row mt-12">{selectedSpecialist.certifications.map((item) => <Badge key={item} tone="success">{item}</Badge>)}</div>
              </Card>
              <Card>
                <h3>Portfolio</h3>
                <div className="stack gap-12 mt-12">{selectedSpecialist.portfolio.map((item) => <div key={item} className="soft-box">{item}</div>)}</div>
              </Card>
            </div>

            <Card className="full-span">
              <h3>Customer Reviews</h3>
              <div className="cards-grid two-cols mt-16">
                {reviews.map((r) => (
                  <div key={r.id} className="review-box">
                    <div className="between-row"><strong>{r.name}</strong><Stars value={r.rating} /></div>
                    <p className="muted mt-12">{r.text}</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {page === 'booking' && (
          <div className="booking-grid">
            <Card>
              <h2>Book Service</h2>
              <div className="soft-box mt-16">
                <strong>{selectedSpecialist.name}</strong>
                <p className="muted small-text">{selectedSpecialist.title}</p>
              </div>
              <div className="double-grid mt-16">
                <div>
                  <label className="field-label">Select Date</label>
                  <div className="field-icon-wrap"><Calendar size={18} /><InputField
                    type="date"
                    value={bookingDate}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setBookingDate(e.target.value)}
                  /></div>
                </div>
                <div>
                  <label className="field-label">Select Time</label>
                  <div className="field-icon-wrap"><Clock size={18} />
                  <InputField
                    type="time"
                    value={bookingTime}
                    min={getMinTime()}
                    onChange={(e) => {
                      const selectedTime = e.target.value;
                      const minTime = getMinTime();

                      if (selectedTime < minTime) {
                        setBookingTime(minTime); // 💥 фикс если выбрали прошлое
                      } else {
                        setBookingTime(selectedTime);
                      }
                    }}
                  /></div>
                </div>
              </div>
              <div className="mt-16">
                <label className="field-label">Describe the service you need</label>
                <TextArea value={serviceDetails} onChange={(e) => setServiceDetails(e.target.value)} />
              </div>
              <Button className="full-width mt-16" onClick={handleBookingConfirm}>Confirm Booking</Button>
            </Card>

            <Card>
              <h2>Price Summary</h2>
              <div className="summary-row mt-16"><span>Service Fee</span><span>${selectedSpecialist.price}</span></div>
              <div className="summary-row"><span>Platform Fee</span><span>$3</span></div>
              <div className="summary-row summary-total"><span>Total</span><span>${selectedSpecialist.price + 3}</span></div>
              <div className="soft-blue-box mt-16">Your booking request will be sent instantly and the specialist will receive a notification.</div>
            </Card>
          </div>
        )}

        {page === 'confirmation' && (
          <div className="centered-page wide">
            <Card className="success-card">
              <div className="success-icon"><CheckCircle2 size={40} /></div>
              <h2>Booking Confirmed!</h2>
              <p className="muted">Your service request has been successfully placed.</p>
              {bookings[0] && (
                <div className="soft-box mt-16 left-text">
                  <p><strong>Order ID:</strong> {bookings[0].id}</p>
                  <p><strong>Specialist:</strong> {bookings[0].specialist}</p>
                  <p><strong>Date & Time:</strong> {bookings[0].date} at {bookings[0].time}</p>
                  <p><strong>Total Price:</strong> ${bookings[0].total}</p>
                </div>
              )}
              <div className="button-row center-row mt-16">
                <Button onClick={() => setPage('tracking')}>Track Order</Button>
                <Button variant="secondary" onClick={() => setPage('home')}>Back to Home</Button>
              </div>
            </Card>
          </div>
        )}

        {page === 'tracking' && (
          <div className="booking-grid">
            <Card>
              <h2>Track Order</h2>
              <div className="soft-box mt-16">
                <p><strong>Order ID:</strong> {bookings[0]?.id ?? 'SKL-1001'}</p>
                <p><strong>Specialist:</strong> {selectedSpecialist.name}</p>
                <p><strong>Service:</strong> {selectedSpecialist.title}</p>
                <p><strong>Date:</strong> {bookingDate}</p>
                <p><strong>Current Status:</strong> {bookingStatus}</p>
              </div>
              <div className="mt-16"><StepTracker status={bookingStatus} /></div>
              <div className="button-row mt-16">
                <Button onClick={advanceStatus}>Advance Status</Button>
                <Button variant="secondary">Contact Specialist</Button>
              </div>
              {bookingStatus === 'Completed' && (
                <div className="success-box mt-16">
                  Service completed successfully. You can now leave a review.
                  <div className="mt-12"><Button onClick={() => setPage('feedback')}>Leave Review</Button></div>
                </div>
              )}
            </Card>

            <Card>
              <h2>Status Timeline</h2>
              <div className="stack gap-12 mt-16">
                <div className="soft-box">Pending — booking request sent to specialist.</div>
                <div className="soft-box">Accepted — specialist confirmed the request.</div>
                <div className="soft-box">In Progress — work is currently being completed.</div>
                <div className="soft-box">Completed — service is finished and ready for feedback.</div>
              </div>
            </Card>
          </div>
        )}

        {page === 'feedback' && (
          <div className="centered-page wide">
            <Card className="auth-card wide-card">
              <h2>Leave a Review</h2>
              <div className="soft-box mt-16">
                <strong>{selectedSpecialist.name}</strong>
                <p className="muted small-text">{selectedSpecialist.title}</p>
              </div>
              <div className="mt-16">
                <label className="field-label">Rate Your Experience</label>
                <div className="star-picker">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <button key={i} className="star-btn" onClick={() => setReviewRating(i + 1)}>
                      <Star size={30} className={i < reviewRating ? 'star active' : 'star'} />
                    </button>
                  ))}
                </div>
              </div>
              <div className="mt-16">
                <label className="field-label">Comment</label>
                <TextArea value={reviewComment} onChange={(e) => setReviewComment(e.target.value)} placeholder="Share your feedback about the service" />
              </div>
              <Button className="full-width mt-16" onClick={submitReview}>Submit Review</Button>
            </Card>
          </div>
        )}

        {page === 'dashboard' && (
          <div className="stack gap-32">
            <div className="cards-grid four-cols">
              {[
                { label: 'Today', value: '$85', icon: DollarSign },
                { label: 'This Week', value: '$420', icon: Briefcase },
                { label: 'This Month', value: '$1,640', icon: Calendar },
                { label: 'Active Jobs', value: String(initialSpecialistJobs.length), icon: Clock },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <Card key={item.label}>
                    <div className="metric-card">
                      <div>
                        <p className="muted small-text">{item.label}</p>
                        <h2>{item.value}</h2>
                      </div>
                      <IconBadge><Icon size={22} /></IconBadge>
                    </div>
                  </Card>
                );
              })}
            </div>

            <Card>
              <SectionHeader title="Active Jobs" />
              <div className="stack gap-12">
                {initialSpecialistJobs.map((job) => (
                  <div key={job.id} className="job-row">
                    <div>
                      <strong>{job.service}</strong>
                      <p className="muted small-text">Client: {job.client}</p>
                      <p className="muted small-text">{job.date} at {job.time}</p>
                    </div>
                    <div className="button-row end-row">
                      <Badge tone="soft">{job.status}</Badge>
                      <Button variant="secondary" onClick={() => setPage('jobs')}>Open Details</Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <SectionHeader title="Notifications" />
              <div className="stack gap-12">
                {['New booking request received.', 'Upcoming job starts in 2 hours.', 'A client left you a 5-star review.'].map((note) => (
                  <div key={note} className="soft-box">{note}</div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {page === 'jobs' && (
          <Card>
            <SectionHeader title="Jobs" />
            <div className="stack gap-12">
              {initialSpecialistJobs.map((job) => (
                <div key={job.id} className="job-row">
                  <div>
                    <strong>{job.service}</strong>
                    <p className="muted small-text">Client: {job.client}</p>
                    <p className="muted small-text">Schedule: {job.date} at {job.time}</p>
                  </div>
                  <Badge tone="soft">{job.status}</Badge>
                </div>
              ))}
            </div>
          </Card>
        )}

        {page === 'bookings' && (
          <Card>
            <SectionHeader title="My Bookings" />
            {bookings.length === 0 ? (
              <div className="empty-state">
                <h3>No Bookings Yet</h3>
                <p className="muted">Start by searching for a service specialist near you.</p>
                <Button onClick={() => setPage('home')}>Explore Services</Button>
              </div>
            ) : (
              <div className="stack gap-12">
                {bookings.map((b) => (
                  <div key={b.id} className="job-row">
                    <div>
                      <strong>{b.service}</strong>
                      <p className="muted small-text">Specialist: {b.specialist}</p>
                      <p className="muted small-text">{b.date} at {b.time}</p>
                    </div>
                    <div className="button-row end-row">
                      <Badge tone="soft">{b.status}</Badge>
                      <Button variant="secondary" onClick={() => setPage('tracking')}>Track</Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {page === 'notifications' && (
          <Card>
            <SectionHeader title="Notifications" />
            <div className="stack gap-12">
              {notifications.map((item) => (
                <div key={item.id} className="notice-row">
                  <IconBadge><Bell size={18} /></IconBadge>
                  <div>
                    <strong>Notification</strong>
                    <p className="muted mt-8">{item.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {page === 'userProfile' && (
          <div className="profile-grid alt-grid">
            <Card>
              <div className="profile-box-center">
                <Avatar name="Alex Johnson" />
                <h2 className="mt-12">Alex Johnson</h2>
                <p className="muted">Client Account</p>
                <div className="stack gap-12 mt-16 full-width">
                  <div className="contact-item"><Mail size={18} className="blue-icon" /> <span>alex@example.com</span></div>
                  <div className="contact-item"><Phone size={18} className="blue-icon" /> <span>+1 555 000 111</span></div>
                  <div className="contact-item"><MapPin size={18} className="blue-icon" /> <span>Downtown Service Area</span></div>
                </div>
              </div>
            </Card>
            <Card>
              <SectionHeader title="Account Overview" />
              <div className="cards-grid two-cols mt-16">
                <div className="soft-box"><p className="muted small-text">Total Bookings</p><h2>{bookings.length}</h2></div>
                <div className="soft-box"><p className="muted small-text">Completed Services</p><h2>{bookingStatus === 'Completed' ? 1 : 0}</h2></div>
              </div>
              <div className="soft-box mt-16">
                <strong>Quick Actions</strong>
                <div className="button-row mt-12">
                  <Button onClick={() => setPage('home')}>Browse Services</Button>
                  <Button variant="secondary" onClick={() => setPage('bookings')}>View Bookings</Button>
                </div>
              </div>
            </Card>
          </div>
        )}
      </main>

      {!['welcome', 'login', 'signup'].includes(page) && (
        <BottomNav
          role={role}
          active={page === 'userProfile' ? 'profile' : ['tracking', 'confirmation', 'feedback', 'listing', 'profile', 'booking'].includes(page) ? (role === 'client' ? 'home' : 'dashboard') : page}
          onNavigate={(target) => {
            if (target === 'profile') {
              setPage('userProfile');
              return;
            }
            setPage(target as Page);
          }}
        />
      )}
    </div>
  );
}
