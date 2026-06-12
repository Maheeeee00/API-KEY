using System;
using UnityEngine;

public class PlayerInventory : MonoBehaviour
{
  [SerializeField] private WeaponDatabase weaponDatabase;
  [SerializeField] private WeaponController weaponController;

  private int medkits;
  private GearLevel backpack = GearLevel.None;

  public int Medkits => medkits;
  public GearLevel Backpack => backpack;
  public WeaponController Weapon => weaponController;

  public event Action OnInventoryChanged;

  public bool TryPickupWeapon(WeaponId weaponId)
  {
    if (weaponDatabase == null || weaponController == null)
    {
      return false;
    }

    weaponController.Equip(weaponDatabase.GetStats(weaponId));
    OnInventoryChanged?.Invoke();
    return true;
  }

  public void AddMedkit(int count = 1)
  {
    int capacity = GetMedkitCapacity();
    medkits = Mathf.Min(capacity, medkits + count);
    OnInventoryChanged?.Invoke();
  }

  public bool TryUseMedkit(PlayerHealth health)
  {
    if (medkits <= 0 || health == null || !health.IsAlive || health.Health >= 100)
    {
      return false;
    }

    medkits--;
    health.Heal(50);
    OnInventoryChanged?.Invoke();
    return true;
  }

  public void SetBackpack(GearLevel level)
  {
    if (level > backpack)
    {
      backpack = level;
      OnInventoryChanged?.Invoke();
    }
  }

  private int GetMedkitCapacity()
  {
    return backpack switch
    {
      GearLevel.Level3 => 8,
      GearLevel.Level2 => 5,
      GearLevel.Level1 => 3,
      _ => 2
    };
  }
}
