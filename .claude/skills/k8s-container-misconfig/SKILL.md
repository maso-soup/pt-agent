---
name: k8s-container-misconfig
description: Discover and exploit exposed Kubernetes management interfaces (kubelet API, dashboard, etcd) and escapable container configurations for an initial cloud foothold. Use when cloud-recon or network-recon finds Kubernetes-related ports/services, or the target is known to run containerized workloads.
---

## Purpose

Kubernetes clusters expose several management surfaces that are frequently
left unauthenticated or under-restricted, and containers themselves are
routinely run with more privilege than needed — both are common, high-impact
initial-foothold and escalation paths into cloud environments.

## When to use

Recon identifies Kubernetes-associated ports (10250 kubelet, 8080/8443
dashboard, 2379 etcd, 6443 API server) or the target's infrastructure is
known/suspected to be container-orchestrated.

## Methodology

1. **Kubelet API** (10250) — check for unauthenticated access; if open, it
   typically allows listing and executing commands in pods directly.
2. **Dashboard** (various ports) — check for missing or default
   authentication; a fully-privileged dashboard is often equivalent to
   cluster-admin.
3. **etcd** (2379) — check for unauthenticated access; etcd holds the entire
   cluster state including secrets, making this one of the highest-impact
   findings possible in a k8s environment.
4. **API server** — check for anonymous/unauthenticated access and
   overly-permissive RBAC bindings once any level of API access exists.
5. **If already inside a container** (from a foothold elsewhere): check for
   privileged mode, mounted host paths/sockets (especially the Docker socket),
   excessive Linux capabilities, and a mounted service account token with
   broad RBAC permissions — any of these can lead to node or cluster
   compromise.

## Tools

- `kubectl` directly against any discovered/authorized API endpoint.
- `kube-hunter` for automated discovery of common Kubernetes
  misconfigurations.
- `kube-bench` for CIS benchmark-style configuration auditing.
- Manual checks inside a container (`mount`, `cat
  /var/run/secrets/kubernetes.io/serviceaccount/token`, capability checks via
  `capsh --print`) once a foothold exists there.

## Output

List of exposed management interfaces with auth status, any pod/cluster
access obtained, and (if applicable) the container escape path and resulting
node/cluster access level.

## Safety notes

- Unauthenticated kubelet/etcd/API access can mean direct control over
  production workloads — confirm the blast radius of any action (don't
  delete/modify running pods) before doing more than read-only enumeration.
- Container escape techniques can affect the underlying node and other
  tenants on shared infrastructure — treat this as high-impact and coordinate
  timing with the client if the cluster is shared/production.
