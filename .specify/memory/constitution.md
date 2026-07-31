# Constitution du projet — publisher-app

## 1. Objectif
- Le projet est un système de gestion d'éditeur (publisher-app) implémenté en Java (Spring Boot) pour le backend, Angular pour le frontend, et PostgreSQL 15 comme base de données.
- Fournir des API REST préfixées /api/v1/... et une expérience de développement testée et cohérente.

## 2. Architecture et couches
- Architecture en couches : Controller -> Service -> Repository -> Entity.
- Utiliser DTOs pour échanges API et MapStruct pour les conversions Entity <-> DTO.
- Les contrôleurs exposent uniquement des DTOs; les entités JPA restent confinées aux couches internes et aux repositories.

## 3. Conventions d'API
- Tous les endpoints REST doivent être préfixés par /api/v1/.
- Toutes les réponses d'API doivent être enveloppées dans ApiResponseDto<T> (success, message, data, meta).
- En cas d'erreur, renvoyer un ApiResponseDto avec code HTTP approprié et message explicite; inclure un errorCode interne lorsque pertinent.

## 4. Authentification et sécurité
- Auth stateless basé sur JWT.
  - Algorithme recommandé : HS256 (clé secrète via variable d'environnement) ou RS256 si paire clé publique/privée.
  - Durée de validité du token : 1 heure (3600s).
  - Utiliser refresh tokens si besoin (hors scope initial) — mais respecter le principe stateless côté API.
- Hashing des mots de passe : BCrypt (strength configurable via application.properties, ex: 10-12).
- Rôles : un seul rôle ADMIN pour cette version. Pas de gestion multi-rôles.
- Protection des endpoints : autorisation par annotation (@PreAuthorize) ou configuration SecurityFilterChain en appliquant la vérification JWT.
- Ne jamais committer de secrets (clés JWT, mots de passe, etc.) dans le dépôt. Les clés vont dans des variables d'environnement, fichiers .env (non commit) ou gestionnaire de secrets.

## 5. Tests et qualité
- Tests unitaires et d'intégration en Java : TestNG.
- Pattern de tests : Factory pattern (ex : BookFactory) pour créer fixtures/tests data.
- Rapports : Allure pour rapports de tests (intégration CI).
- Couverture : viser couverture significative sur les services/logic métier; les contrôleurs peuvent être testés via tests d'intégration.
- Frontend : utiliser les frameworks de tests Angular (Karma/Jasmine ou Jest selon configuration) et tests E2E si prévus.

## 6. Conventions de commits et gestion de branches
- Aucun commit direct sur main.
- Toujours passer par une Pull Request (PR) pour fusionner sur main.
- Branches : feature/<ticket>-<brève-description>, fix/<ticket>-..., chore/<...>.
- PR doit contenir : description, liens vers tickets, checklist de tests exécutés, notes UI si pertinent.
- Configurer protection de branche main (required status checks, review minimum 1+, ne pas autoriser pushes directs).

## 7. CI / Validation automatique (recommandations)
- CI doit exécuter :
  - Build backend (mvn -T1C clean package)
  - Exécuter tests unitaires (mvn test) et générer rapport Allure
  - Linter/TypeCheck pour frontend (npm ci && npm run build/test)
  - Vérification qu'aucun secret n'est committé (git-secrets / truffleHog optionnel)
  - Statuts CI doivent passer avant merge

## 8. Documentation et fichiers recommandés
- README.md : commandes rapides (build, run, test).
- CONTRIBUTING.md : workflow de branche/PR, conventions de commit.
- SECURITY.md : procédure pour signaler vulnérabilités et gestion des secrets.
- Ajouter CONSTITUTION.md (ce document) à la racine pour référence.
- Exemple de snippet JWT config dans application.properties (voir section Exemples rapides).

## 9. Exemples rapides (configuration/implémentation)
- application.properties (extraits via variables d'environnement) :
  - jwt.secret=${JWT_SECRET}
  - jwt.expiration=3600
  - spring.datasource.url=jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}
- Hashage BCrypt (Spring) :
  - @Bean public PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(10); }
- Envelope ApiResponseDto<T> : fields typiques { boolean success; String message; T data; Map<String,Object> meta; }

## 10. Gouvernance et workflow
- Revue de code obligatoire via PR.
- Tests unitaires/integration obligatoires pour toute logique métier ajoutée.
- Ajout ou modification de schéma DB doit être accompagné de scripts de migration (Flyway/Liquibase) et tests d'intégration.

## 11. Notes complémentaires
- Prévoir versioning d'API (/api/v2/...) pour ruptures futures.
- Pour l'auth, prévoir extension User/Role mais ne pas activer multi-roles pour cette version.
- Respect RGPD si le projet traite de données personnelles (pseudonymisation/consentement).

---

Checklist rapide avant merge d'une nouvelle fonctionnalité :
- [ ] Code compilé et buildé localement
- [ ] Tests unitaires/integ exécutés et passing
- [ ] Allure report généré (si applicable)
- [ ] Pas de secrets committés
- [ ] PR avec description et checklist
- [ ] Au moins 1 approbation de revue
- [ ] CI status checks passed
