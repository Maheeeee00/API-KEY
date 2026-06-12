using UnityEngine;
using UnityEngine.AI;

[RequireComponent(typeof(NavMeshAgent))]
public class EnemyAI : MonoBehaviour
{
  private enum BotState
  {
    Looting,
    RunningToZone,
    Attacking,
    SeekingCover
  }

  [SerializeField] private float lootSearchRadius = 60f;
  [SerializeField] private float attackRange = 30f;
  [SerializeField] private float coverSearchRadius = 15f;
  [SerializeField] private float fireAccuracy = 0.65f;
  [SerializeField] private float stateReevaluateInterval = 0.5f;

  private NavMeshAgent agent;
  private BotHealth health;
  private BotInventory inventory;
  private BotVision vision;
  private Transform attackTarget;
  private BotState currentState = BotState.Looting;
  private float nextStateCheck;
  private float nextShotTime;
  private Vector3 coverPoint;

  private void Awake()
  {
    agent = GetComponent<NavMeshAgent>();
    health = GetComponent<BotHealth>();
    inventory = GetComponent<BotInventory>();
    vision = GetComponent<BotVision>();
  }

  private void Update()
  {
    if (health == null || !health.IsAlive)
    {
      return;
    }

    if (Time.time >= nextStateCheck)
    {
      EvaluateState();
      nextStateCheck = Time.time + stateReevaluateInterval;
    }

    switch (currentState)
    {
      case BotState.Looting:
        UpdateLooting();
        break;
      case BotState.RunningToZone:
        UpdateRunningToZone();
        break;
      case BotState.Attacking:
        UpdateAttacking();
        break;
      case BotState.SeekingCover:
        UpdateSeekingCover();
        break;
    }
  }

  private void EvaluateState()
  {
    bool outsideZone = ZoneManager.Instance != null && !ZoneManager.Instance.IsInsideSafeZone(transform.position);
    if (outsideZone)
    {
      currentState = BotState.RunningToZone;
      return;
    }

    if (vision != null && vision.TryFindTarget(out Transform target))
    {
      attackTarget = target;
      currentState = BotState.Attacking;
      return;
    }

    if (health.Health < 40 && inventory != null && inventory.Medkits > 0)
    {
      inventory.TryUseMedkit(health);
    }

    if (!inventory.HasWeapon)
    {
      currentState = BotState.Looting;
      return;
    }

    if (attackTarget != null && vision.CanSee(attackTarget) && Random.value < 0.3f)
    {
      currentState = BotState.SeekingCover;
      coverPoint = FindCoverPosition();
      return;
    }

    currentState = BotState.Looting;
  }

  private void UpdateLooting()
  {
    Vector3 lootPosition = FindNearestLoot();
    if (lootPosition != Vector3.zero)
    {
      agent.isStopped = false;
      agent.SetDestination(lootPosition);
    }
    else if (ZoneManager.Instance != null)
    {
      agent.SetDestination(ZoneManager.Instance.GetSafeZoneCenter());
    }
  }

  private void UpdateRunningToZone()
  {
    if (ZoneManager.Instance == null)
    {
      return;
    }

    agent.isStopped = false;
    agent.SetDestination(ZoneManager.Instance.GetSafeZoneCenter());
  }

  private void UpdateAttacking()
  {
    if (attackTarget == null || !vision.CanSee(attackTarget))
    {
      currentState = BotState.Looting;
      return;
    }

    float distance = Vector3.Distance(transform.position, attackTarget.position);
    if (distance > attackRange)
    {
      agent.isStopped = false;
      agent.SetDestination(attackTarget.position);
    }
    else
    {
      agent.isStopped = true;
      Vector3 lookTarget = attackTarget.position;
      lookTarget.y = transform.position.y;
      transform.LookAt(lookTarget);
      ShootAtTarget();
    }
  }

  private void UpdateSeekingCover()
  {
    agent.isStopped = false;
    agent.SetDestination(coverPoint);

    if (Vector3.Distance(transform.position, coverPoint) < 1.5f)
    {
      currentState = BotState.Attacking;
    }
  }

  private void ShootAtTarget()
  {
    if (inventory == null || !inventory.HasWeapon || attackTarget == null)
    {
      return;
    }

    if (Time.time < nextShotTime)
    {
      return;
    }

    nextShotTime = Time.time + inventory.Weapon.Stats.fireRate;

    if (Random.value > fireAccuracy)
    {
      return;
    }

    Vector3 origin = transform.position + Vector3.up * 1.6f;
    Vector3 direction = (attackTarget.position + Vector3.up * 1.2f - origin).normalized;
    inventory.Weapon.TryFire(origin, direction, gameObject);
  }

  private Vector3 FindNearestLoot()
  {
    Collider[] hits = Physics.OverlapSphere(transform.position, lootSearchRadius);
    float bestDistance = float.MaxValue;
    Vector3 bestPosition = Vector3.zero;

    foreach (Collider hit in hits)
    {
      if (!hit.CompareTag("Loot"))
      {
        continue;
      }

      float distance = Vector3.Distance(transform.position, hit.transform.position);
      if (distance < bestDistance)
      {
        bestDistance = distance;
        bestPosition = hit.transform.position;
      }
    }

    return bestPosition;
  }

  private Vector3 FindCoverPosition()
  {
    for (int i = 0; i < 6; i++)
    {
      Vector3 randomOffset = Random.insideUnitSphere * coverSearchRadius;
      randomOffset.y = 0f;
      Vector3 candidate = transform.position + randomOffset;

      if (NavMesh.SamplePosition(candidate, out NavMeshHit navHit, 3f, NavMesh.AllAreas))
      {
        if (attackTarget == null || Vector3.Distance(navHit.position, attackTarget.position) > 8f)
        {
          return navHit.position;
        }
      }
    }

    return transform.position;
  }
}
