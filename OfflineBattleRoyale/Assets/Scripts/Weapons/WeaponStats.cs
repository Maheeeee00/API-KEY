using System;
using UnityEngine;

[Serializable]
public class WeaponStats
{
  public WeaponId id;
  public string displayName;
  public WeaponType type;
  public int damage = 25;
  public float fireRate = 0.15f;
  public float range = 100f;
  public int magazineSize = 30;
  public float reloadTime = 2f;
  public float spread = 2f;
}
