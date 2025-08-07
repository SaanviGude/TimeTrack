import Navbar from '../components/Navbar';
import HeroSection from '../components/HeroSection';
import FeaturesSection from '../components/FeaturesSection';
import Footer from '../components/Footer';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-white"> 
      <Navbar />
      <HeroSection />
      <FeaturesSection /> 
      <Footer />
      {/* Test Tailwind */}

    </main>
  );
}

