import React from 'react';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';
import HeroSection from '../components/home/HeroSection';
import FeaturesSection from '../components/home/FeaturesSection';
import HowItWorksSection from '../components/home/HowItWorksSection';
import TestimonialsSection from '../components/home/TestimonialsSection';
import { AuroraGradientBackground } from '../components/ui/ParticlesBackground';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      <Navbar />
      <div className="relative">
        <AuroraGradientBackground />
        <div className="relative z-10">
          <HeroSection />
          <FeaturesSection />
          <HowItWorksSection />
          <TestimonialsSection />
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Home;