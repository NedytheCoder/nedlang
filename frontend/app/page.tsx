import Navbar from "./components/landing/Navbar"
import Hero from "./components/landing/Hero"
import GamifiedSection from "./components/landing/GamifiedSection"
import FrameworkSection from "./components/landing/FrameworkSection"
import HowItWorks from "./components/landing/HowItWorks"
import Testimonials from "./components/landing/Testimonials"
import Footer from "./components/landing/Footer"

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <GamifiedSection />
        <FrameworkSection />
        <HowItWorks />
        <Testimonials />
      </main>
      <Footer />
    </>
  )
}
