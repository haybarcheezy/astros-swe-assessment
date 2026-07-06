# Development practices questions

Please provide thoughtful responses to the following questions. Your answers should demonstrate your understanding of modern development practices and architectural considerations.

## DevOps Practices

### 1. CI/CD Pipeline Design

**Question:** How do you design CI/CD pipelines for applications like this? What are your must-have checks?

**Your Answer:**

I think of CI and CD as answering two different questions: "is this change safe to merge?" and "is this artifact safe to promote?" At JPMC I worked with Jules (our Jenkins-based CI) and Spinnaker for delivery, and that separation is the part I'd carry over to any stack, including the GitHub Actions workflow I added to this repo.

For CI, my must-haves in order of how fast they fail:

- Lint and type checks first (ruff/eslint/tsc) for seconds of feedback before anything expensive runs
- Unit and integration tests for both halves of the app. For this project that's pytest against a seeded in-memory DB and vitest with a mocked API layer
- Dependency and secret scanning
- Build the deployable artifact (Docker image) in CI, tag it immutably (e.g., with the commit SHA | internal-artifactory-repo.com/repo-image@sha256:sha123456asdf | intead of internal-artifactory-repo.com/repo-image:latest), and promote that same image through every environment.

For CD, my preference is blue-green. On my last project we deployed the green stack alongside blue, pointed a smoke domain at it, ran verification against real infrastructure, and only then cut Route53 over to the new stack. Rollback is just pointing DNS back. Deploys stop being scary when the rollback story is that simple.

### 2. Infrastructure as Code

**Question:** How would you approach infrastructure-as-code for deploying this project in a cloud environment?

**Your Answer:**

Terraform is my daily driver. I just finished migrating our EKS stack to a modular Terraform layout at JPMC, so this is fresh. The lesson from that migration: structure the code as reusable modules (network, compute, database, DNS) with thin per-environment compositions on top, so dev/staging/prod differ only in variables (variables/local.tfvars, variables/dev.tfvars, etc..), never in topology. When environments share modules, drift between them basically disappears.

For this project specifically I'd keep it deliberately boring: containerize both services, push images to ECR, run them on ECS Fargate behind an ALB, and swap SQLite for RDS Postgres the moment we need more than one instance. I have plenty of EKS experience and I still wouldn't reach for it here. Kubernetes for a two-service CRUD app would just be operational overhead.

Process-wise: remote state with locking, `terraform plan` posted on every infra PR so the diff gets reviewed like code, and `apply` only from the pipeline with short-lived OIDC credentials never from laptops. Everything auditable through Git history. kubectl commands only executable by the pipeline, never from a dev machine. These kubectl commands could be executed as part of a spinnaker pipeline, or a GitHub Actions workflow that runs on merge to main. The key is that the pipeline is the only thing that can change production.

### 3. Monitoring and Alerting

**Question:** What strategies do you recommend for monitoring and alerting in production?

**Your Answer:**

Alert on symptoms, not causes. A 5xx spike or latency burn on `/api/pitches` should ping someone; CPU at 80% should not, that's a dashboard, not a page. I anchor on RED metrics (rate, errors, duration) per endpoint, with SLO burn-rate alerts instead of static thresholds, because static thresholds either fire constantly or never.

The three pillars I set up on every service: structured JSON logs with request IDs so you can trace a single request through the system, metrics into something like Prometheus/CloudWatch, and distributed tracing once there's more than one service in the request path.

Two practical things I learned running production systems: liveness and readiness need to be separate checks (this app's `/health` is the seed of that, readiness should actually touch the DB), and every alert must be actionable. An alert channel the team has muted is worse than no alerts at all, because it manufactures false confidence. When we cut over from NGINX to ALB, having the ALB's target-group health checks and request metrics wired into dashboards before the migration is what let us verify the green stack confidently on the smoke domain.

## Legacy Systems

### 4. Legacy Modernization

**Question:** Walk through your process for modernizing a legacy codebase with minimal disruption.

**Your Answer:**

I'll use a real one: at JPMC I led decommissioning our NGINX ingress layer in favor of ALBs, alongside restructuring the EKS stack into modular Terraform. The process I follow:

1. **Characterize before you change.** You can't safely modify what you can't verify. Capture current behavior first: tests where possible, traffic/config audits where not. For the NGINX work that meant inventorying every routing rule, header rewrite, and timeout the old layer was silently providing.
2. **Build the new path alongside the old.** Strangler-fig, not big-bang. We stood up the ALB stack in parallel while NGINX kept serving production.
3. **Verify on real infrastructure before real users.** We pointed a smoke domain at the green stack and ran verification against it (actual TLS, actual routing, actual targets), not a staging approximation.
4. **Make the cutover boring and reversible.** Route53 switch to the new stack once green verified. Rollback plan was the same switch in reverse. Decommission (terraform purge) the old path only after the new one has soaked.
5. **Data changes last and slowest.** Schema migrations get expand-and-contract: add new alongside old, dual-write, backfill, verify, then remove.

A miniature version of this thinking is in this repo: the pitches table stores numerics as TEXT, and instead of stopping to re-ingest the database, I cast at the query layer and coerce types at the serialization boundary. Correct behavior now, with a documented migration path for later.

## Testing

### 5. Test Suite Organization

**Question:** What patterns and practices inform your test suite organization?

**Your Answer:**

I weight my investment toward integration-level tests that exercise real seams, with unit tests reserved for genuinely tricky logic (closer to the "testing trophy" than the classic pyramid). In this repo the backend tests run the Flask test client against a seeded in-memory SQLite database: real routing, real SQL, real serialization. That's the layer where bugs actually live. The velocity-filter CAST bug would sail straight through mocked unit tests.

Principles I hold the line on:

- Test observable behavior, not implementation. The frontend tests query the DOM the way a user would (Testing Library), so refactors don't break them
- Fixtures should be small and explicit. My seed data is a handful of hand-written rows, including one pitch with a blank velocity, because the real data has them and the null path deserves coverage
- Test names should read as specifications: `test_filter_by_min_velocity_casts_text_column` tells you what broke without opening the file
- The suite has to be fast enough to run on every save (the backend suite here runs in under a second), or people stop running it. Mirror the source structure so navigation is mechanical

## Architecture

### 6. Scaling Architecture

**Question:** What architectural choices would you make if tasked to scale this system for millions of daily active users?

**Your Answer:**

First characterize the workload, because it changes everything: this is read-heavy and append-mostly. Pitch data arrives per game and historical rows never change. That's the easy kind of scaling problem, and it rewards boring architecture:

1. SQLite -> Postgres (RDS) with read replicas, proper column types, and indexes on pitcher, batter, and game_date
2. Cache aggressively. Completed-season data is immutable, so aggregate endpoints like the arsenal summary can sit at the CDN edge with long TTLs; ETags on the tables
3. Precompute aggregates in materialized views or a nightly job instead of running GROUP BY per request
4. Stateless API scaled horizontally behind an ALB (the app-factory refactor in this repo is what makes that possible), static frontend on a CDN
5. Swap offset pagination for cursor pagination once tables get deep. OFFSET 500000 does the work of reading half a million rows to throw them away

What I wouldn't do is jump to microservices or a distributed database. A well-indexed Postgres with a cache in front serves millions of DAU for a dataset like this. Having spent the last stretch of my career operating Kubernetes, my honest takeaway is that you should earn that complexity with evidence, not adopt it as a default.

## Opinion

### 7. Overrated Practice

**Question:** What's one commonly-used pattern/practice you think is overrated, and what alternative do you recommend?

**Your Answer:**

Code-coverage percentage targets. Once a team is chasing "90%", people write tests that execute code without meaningfully asserting on it: snapshot dumps, mocked-to-death units, tests that literally cannot fail. That's worse than no metric, because it manufactures confidence that isn't there. Coverage measures execution, not verification.

What I do instead: treat coverage as a diff-level ratchet ("new logic ships with tests") rather than a repo-wide scoreboard, review what tests assert during code review with the same seriousness as the code itself, and occasionally spot-check with mutation testing. If you can flip a comparison operator and the suite stays green, the number was lying to you. I'd rather own 70% coverage where every test would genuinely catch a regression than 95% that's theater.
