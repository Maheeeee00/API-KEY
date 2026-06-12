using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "WeaponDatabase", menuName = "BattleRoyale/Weapon Database")]
public class WeaponDatabase : ScriptableObject
{
  public List<WeaponStats> weapons = new List<WeaponStats>
  {
    new WeaponStats { id = WeaponId.AK47, displayName = "AK47", type = WeaponType.AssaultRifle, damage = 28, fireRate = 0.12f, range = 120f, magazineSize = 30, reloadTime = 2.2f, spread = 2.5f },
    new WeaponStats { id = WeaponId.SCAR, displayName = "SCAR", type = WeaponType.AssaultRifle, damage = 26, fireRate = 0.1f, range = 130f, magazineSize = 30, reloadTime = 2f, spread = 2f },
    new WeaponStats { id = WeaponId.MP40, displayName = "MP40", type = WeaponType.SubmachineGun, damage = 18, fireRate = 0.07f, range = 60f, magazineSize = 40, reloadTime = 1.8f, spread = 3f },
    new WeaponStats { id = WeaponId.M1014, displayName = "M1014", type = WeaponType.Shotgun, damage = 12, fireRate = 0.8f, range = 25f, magazineSize = 8, reloadTime = 3f, spread = 8f },
    new WeaponStats { id = WeaponId.AWM, displayName = "AWM", type = WeaponType.Sniper, damage = 90, fireRate = 1.5f, range = 250f, magazineSize = 5, reloadTime = 3.5f, spread = 0.5f }
  };

  public WeaponStats GetStats(WeaponId id)
  {
    foreach (WeaponStats stats in weapons)
    {
      if (stats.id == id)
      {
        return stats;
      }
    }

    return weapons[0];
  }
}
