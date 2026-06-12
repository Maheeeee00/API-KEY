using UnityEngine;

public class WeaponController : MonoBehaviour
{
  [SerializeField] private Transform muzzle;
  [SerializeField] private LayerMask hitMask = ~0;

  private WeaponStats stats;
  private int ammoInMag;
  private float nextFireTime;
  private bool isReloading;
  private float reloadEndTime;

  public WeaponStats Stats => stats;
  public int AmmoInMag => ammoInMag;
  public bool IsReloading => isReloading;

  public void Equip(WeaponStats weaponStats)
  {
    stats = weaponStats;
    ammoInMag = stats.magazineSize;
    isReloading = false;
    nextFireTime = 0f;
  }

  public bool TryFire(Camera aimCamera, GameObject attacker)
  {
    if (aimCamera != null)
    {
      return TryFire(aimCamera.transform.position, aimCamera.transform.forward, attacker);
    }

    return TryFire(transform.position, transform.forward, attacker);
  }

  public bool TryFire(Vector3 origin, Vector3 direction, GameObject attacker)
  {
    if (stats == null || isReloading || Time.time < nextFireTime)
    {
      return false;
    }

    if (ammoInMag <= 0)
    {
      TryReload();
      return false;
    }

    ammoInMag--;
    nextFireTime = Time.time + stats.fireRate;

    direction = ApplySpread(direction.normalized, stats.spread);

    if (stats.type == WeaponType.Shotgun)
    {
      FirePellets(origin, direction, attacker, 8);
    }
    else
    {
      FireRay(origin, direction, attacker);
    }

    return true;
  }

  public bool TryReload()
  {
    if (stats == null || isReloading || ammoInMag >= stats.magazineSize)
    {
      return false;
    }

    isReloading = true;
    reloadEndTime = Time.time + stats.reloadTime;
    return true;
  }

  private void Update()
  {
    if (isReloading && Time.time >= reloadEndTime)
    {
      ammoInMag = stats.magazineSize;
      isReloading = false;
    }
  }

  private void FirePellets(Vector3 origin, Vector3 direction, GameObject attacker, int pelletCount)
  {
    for (int i = 0; i < pelletCount; i++)
    {
      Vector3 pelletDirection = ApplySpread(direction, stats.spread * 2f);
      FireRay(origin, pelletDirection, attacker);
    }
  }

  private void FireRay(Vector3 origin, Vector3 direction, GameObject attacker)
  {
    if (Physics.Raycast(origin, direction, out RaycastHit hit, stats.range, hitMask, QueryTriggerInteraction.Ignore))
    {
      IDamageable damageable = hit.collider.GetComponentInParent<IDamageable>();
      damageable?.TakeDamage(stats.damage, attacker);
    }
  }

  private static Vector3 ApplySpread(Vector3 direction, float spreadDegrees)
  {
    return Quaternion.Euler(
      Random.Range(-spreadDegrees, spreadDegrees),
      Random.Range(-spreadDegrees, spreadDegrees),
      0f
    ) * direction;
  }
}
