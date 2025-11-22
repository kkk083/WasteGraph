-- Table des nœuds
CREATE TABLE IF NOT EXISTS nodes (
    id VARCHAR(50) PRIMARY KEY,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    capacity INTEGER DEFAULT 0
);

-- Table des arêtes (SANS constraint_value maintenant)
CREATE TABLE IF NOT EXISTS edges (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    target VARCHAR(50) NOT NULL,
    weight FLOAT NOT NULL,
    FOREIGN KEY (source) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target) REFERENCES nodes(id) ON DELETE CASCADE,
    UNIQUE(source, target)
);

-- NOUVELLE : Table des contraintes avec cycle de vie
CREATE TABLE IF NOT EXISTS constraints (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    target VARCHAR(50) NOT NULL,
    constraint_value FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_days INTEGER,
    expires_at TIMESTAMP,
    FOREIGN KEY (source) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (target) REFERENCES nodes(id) ON DELETE CASCADE
);

-- NOUVELLE : Historique des calculs de chemins
CREATE TABLE IF NOT EXISTS path_history (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    destination VARCHAR(50) NOT NULL,
    path TEXT NOT NULL,
    distance FLOAT NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    constraints_snapshot TEXT,
    user_notes TEXT,
    FOREIGN KEY (source) REFERENCES nodes(id),
    FOREIGN KEY (destination) REFERENCES nodes(id)
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target);
CREATE INDEX IF NOT EXISTS idx_constraints_active ON constraints(is_active);
CREATE INDEX IF NOT EXISTS idx_constraints_expires ON constraints(expires_at);
CREATE INDEX IF NOT EXISTS idx_path_history_date ON path_history(calculated_at);
CREATE INDEX IF NOT EXISTS idx_path_history_route ON path_history(source, destination);