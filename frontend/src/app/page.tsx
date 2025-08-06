import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import Footer from '../components/Footer';

// Inside src/app/page.tsx
export default function LandingPage() {
  return (
    <main> 
      <Navbar />
      <HeroSection />
      <FeaturesSection /> 
      <Footer />
      {/* ... other sections ... */}
    </main>
  );
}

