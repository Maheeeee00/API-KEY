using System.Collections.Generic;
using UnityEngine;

public static class WeaponModelMapping
{
  public static readonly Dictionary<WeaponId, string> ModelFileNames = new Dictionary<WeaponId, string>
  {
    { WeaponId.AK47, "AssaultRifle_1.fbx" },
    { WeaponId.SCAR, "AssaultRifle_2.fbx" },
    { WeaponId.MP40, "SubmachineGun_1.fbx" },
    { WeaponId.M1014, "Shotgun_1.fbx" },
    { WeaponId.AWM, "SniperRifle_1.fbx" }
  };

  public static string GetModelFileName(WeaponId id)
  {
    return ModelFileNames.TryGetValue(id, out string fileName) ? fileName : "AssaultRifle_1.fbx";
  }
}
