using UnityEngine;

public class SafeZoneDamage : MonoBehaviour
{
  [SerializeField] private float tickInterval = 1f;

  private IDamageable damageable;
  private float nextTickTime;

  private void Awake()
  {
    damageable = GetComponent<IDamageable>();
  }

  private void Update()
  {
    if (damageable == null || !damageable.IsAlive || ZoneManager.Instance == null)
    {
      return;
    }

    if (ZoneManager.Instance.IsInsideSafeZone(transform.position))
    {
      return;
    }

    if (Time.time < nextTickTime)
    {
      return;
    }

    nextTickTime = Time.time + tickInterval;
    int damage = Mathf.RoundToInt(ZoneManager.Instance.OutsideDamagePerSecond * tickInterval);
    damageable.TakeDamage(damage, null);
  }
}
