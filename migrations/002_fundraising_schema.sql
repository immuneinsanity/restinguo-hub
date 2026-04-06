-- Fundraising schema for Restinguo Hub

CREATE TABLE IF NOT EXISTS investors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,
    firm TEXT NOT NULL,
    fund_focus TEXT,
    stage_focus TEXT,
    typical_check_size TEXT,
    contact_name TEXT,
    contact_email TEXT,
    contact_linkedin TEXT,
    source TEXT,
    status TEXT NOT NULL DEFAULT 'Not Contacted'
        CHECK (status IN ('Not Contacted','Researching','Reached Out','Meeting Scheduled','In Diligence','Term Sheet','Pass','Invested')),
    priority INTEGER DEFAULT 3,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS investor_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    investor_id UUID NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type TEXT NOT NULL DEFAULT 'Note'
        CHECK (type IN ('Email','Call','Meeting','Intro','Note','Other')),
    notes TEXT,
    next_action TEXT,
    next_action_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS funding_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company TEXT NOT NULL,
    amount TEXT,
    stage TEXT,
    date DATE,
    investors TEXT,
    disease_area TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comparables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company TEXT NOT NULL,
    description TEXT,
    raised_amount TEXT,
    stage_at_raise TEXT,
    year INTEGER,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-update updated_at for investors
CREATE OR REPLACE FUNCTION update_investors_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS investors_updated_at ON investors;
CREATE TRIGGER investors_updated_at
    BEFORE UPDATE ON investors
    FOR EACH ROW EXECUTE FUNCTION update_investors_updated_at();

-- Seed: target investors
INSERT INTO investors (firm, name, fund_focus, stage_focus, typical_check_size, source, status, priority, notes) VALUES
('Atlas Venture', NULL, 'Rare disease, biotech, drug discovery', 'Seed, Series A', '$2-10M', 'Known rare disease investor', 'Not Contacted', 1, 'Strong rare disease track record. Boston-based.'),
('RA Capital Management', NULL, 'Biotech, rare disease, public + private', 'Series A, B', '$10-50M', 'Known rare disease investor', 'Not Contacted', 1, 'Deep science focus, rare disease expertise, long-term holders.'),
('Vida Ventures', NULL, 'Rare disease, precision medicine', 'Seed, Series A', '$5-20M', 'Known rare disease investor', 'Not Contacted', 1, 'Specifically focuses on rare and ultra-rare diseases.'),
('5AM Ventures', NULL, 'Biotech, rare disease, early stage', 'Seed, Series A', '$2-15M', 'Known rare disease investor', 'Not Contacted', 1, 'Very early stage friendly, rare disease portfolio.'),
('Foresite Capital', NULL, 'Biotech, genomics, rare disease', 'Series A, B', '$10-50M', 'Known rare disease investor', 'Not Contacted', 2, 'Data-driven biotech investor, rare disease focus.'),
('OrbiMed', NULL, 'Healthcare, biotech, rare disease', 'Series A, B, C', '$10-100M', 'Known rare disease investor', 'Not Contacted', 2, 'Large dedicated healthcare fund, global reach.'),
('Deerfield Management', NULL, 'Healthcare, biotech, rare disease', 'Series A, B', '$10-50M', 'Known rare disease investor', 'Not Contacted', 2, 'Philanthropy arm funds early rare disease research too.'),
('Third Rock Ventures', NULL, 'Biotech, drug discovery, rare disease', 'Seed, Series A', '$10-30M', 'Known rare disease investor', 'Not Contacted', 1, 'Company builder model, very early stage, rare disease strong suit.'),
('Versant Ventures', NULL, 'Biotech, rare disease, early stage', 'Seed, Series A', '$5-25M', 'Known rare disease investor', 'Not Contacted', 2, 'Early stage biotech, rare disease portfolio includes several interferonopathy-adjacent companies.'),
('Apple Tree Partners', NULL, 'Rare disease, biotech', 'Seed, Series A', '$5-20M', 'Known rare disease investor', 'Not Contacted', 1, 'Dedicated rare disease fund. Very relevant.'),
('MPM Capital', NULL, 'Biotech, rare disease, oncology', 'Series A, B', '$10-30M', 'Known rare disease investor', 'Not Contacted', 2, 'Long-standing biotech fund, rare disease experience.'),
('Sofinnova Partners', NULL, 'Biotech, rare disease, European', 'Seed, Series A', '$5-20M', 'Known rare disease investor', 'Not Contacted', 2, 'European focus but US deals too, rare disease specialist.'),
('Polaris Partners', NULL, 'Biotech, healthcare, rare disease', 'Seed, Series A', '$5-20M', 'Known rare disease investor', 'Not Contacted', 2, 'Boston-based, strong biotech network.'),
('F-Prime Capital', NULL, 'Biotech, rare disease, early stage', 'Seed, Series A', '$2-15M', 'Known rare disease investor', 'Not Contacted', 2, 'Fidelity-affiliated, early stage biotech.'),
('Novo Holdings', NULL, 'Biotech, rare disease, pharma', 'Series A, B', '$10-50M', 'Known rare disease investor', 'Not Contacted', 2, 'Novozymes/Novo Nordisk affiliated, rare disease mission alignment.'),
('Alexandria Venture Investments', NULL, 'Biotech, life sciences, early stage', 'Seed, Series A', '$1-10M', 'Known rare disease investor', 'Not Contacted', 3, 'CVC arm of Alexandria Real Estate, good network.'),
('Canaan Partners', NULL, 'Biotech, healthcare, early stage', 'Seed, Series A', '$2-10M', 'Known rare disease investor', 'Not Contacted', 3, 'Early stage healthcare and biotech.'),
('PureTech Health', NULL, 'Biotech, rare disease, inflammation', 'Seed, Series A', '$5-20M', 'Known rare disease investor', 'Not Contacted', 2, 'Inflammation and rare disease focus, company builder.')
ON CONFLICT DO NOTHING;

-- Seed: comparable companies
INSERT INTO comparables (company, description, raised_amount, stage_at_raise, year, notes) VALUES
('ImmuneSensor Therapeutics', 'cGAS inhibitor (IMSB301) for AGS and interferonopathies, Phase 1b', '$10M Series A', 'Pre-clinical/Phase 1', 2023, 'Competitor — different MOA (cGAS upstream vs IFNAR downstream). Raised small Series A.'),
('Alumis', 'Oral TYK2 inhibitor for autoimmune/interferonopathies', '$200M Series B', 'Phase 2', 2022, 'Different target but same disease area. Shows investor appetite for IFN pathway.'),
('Protagonist Therapeutics', 'Peptide drugs for rare hematologic diseases', '$100M+', 'Phase 2', 2020, 'Rare disease, showed path from target validation to clinical.'),
('Imvax', 'Rare CNS disease, early stage', '$60M Series B', 'Pre-clinical', 2021, 'Comparable rare disease seed/Series A trajectory.'),
('Navire Pharma', 'SHP2 inhibitor, rare oncology', '$108M Series B', 'Pre-clinical', 2020, 'Early mechanism validation → large raise. Good comp for Restinguo trajectory.')
ON CONFLICT DO NOTHING;

-- Seed: funding events
INSERT INTO funding_events (company, amount, stage, date, investors, disease_area, notes) VALUES
('ImmuneSensor Therapeutics', '$10M', 'Series A', '2023-01-01', 'Undisclosed', 'Interferonopathy / AGS', 'cGAS inhibitor, first patient dosed Feb 2026 in Phase 1b'),
('Alumis', '$200M', 'Series B', '2022-06-01', 'Multiple VCs', 'Autoimmune / TYK2', 'Large raise validates IFN pathway investor interest'),
('Sironax', '$100M', 'Series B', '2021-09-01', 'Multiple', 'STING pathway', 'STING inhibitor program, validates pathway investment'),
('Protagonist Therapeutics', '$75M', 'Series C', '2020-03-01', 'Multiple', 'Rare hematologic', 'Shows rare disease financing trajectory'),
('Imago BioSciences', '$55M', 'Series B', '2019-01-01', 'Multiple', 'Rare hematologic', 'Pre-clinical to Series B, rare disease playbook')
ON CONFLICT DO NOTHING;
