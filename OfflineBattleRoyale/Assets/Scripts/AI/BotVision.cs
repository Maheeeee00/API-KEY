using UnityEngine;

public class BotVision : MonoBehaviour
{
  [SerializeField] private float sightRange = 35f;
  [SerializeField] private float fieldOfView = 110f;
  [SerializeField] private LayerMask obstructionMask = ~0;

  public Transform CurrentTarget { get; private set; }

  public bool TryFindTarget(out Transform target)
  {
    target = null;
    float bestDistance = sightRange;

    Collider[] hits = Physics.OverlapSphere(transform.position, sightRange);
    foreach (Collider hit in hits)
    {
      if (hit.transform == transform)
      {
        continue;
      }

      IDamageable damageable = hit.GetComponentInParent<IDamageable>();
      if (damageable == null || !damageable.IsAlive)
      {
        continue;
      }

      Vector3 direction = hit.transform.position - transform.position;
      if (Vector3.Angle(transform.forward, direction) > fieldOfView * 0.5f)
      {
        continue;
      }

      if (Physics.Raycast(transform.position + Vector3.up, direction.normalized, out RaycastHit rayHit, sightRange, obstructionMask, QueryTriggerInteraction.Ignore))
      {
        if (rayHit.collider.transform.root != hit.transform.root)
        {
          continue;
        }
      }

      float distance = direction.magnitude;
      if (distance < bestDistance)
      {
        bestDistance = distance;
        target = hit.transform;
      }
    }

    CurrentTarget = target;
    return target != null;
  }

  public bool CanSee(Transform target)
  {
    if (target == null)
    {
      return false;
    }

    Vector3 direction = target.position - transform.position;
    if (direction.magnitude > sightRange)
    {
      return false;
    }

    if (Vector3.Angle(transform.forward, direction) > fieldOfView * 0.5f)
    {
      return false;
    }

    return !Physics.Raycast(transform.position + Vector3.up, direction.normalized, out RaycastHit hit, sightRange, obstructionMask, QueryTriggerInteraction.Ignore)
      || hit.transform.root == target.root;
  }
}
