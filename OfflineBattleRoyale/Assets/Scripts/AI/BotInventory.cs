using UnityEngine;

public class BotInventory : MonoBehaviour
{
  [SerializeField] private WeaponDatabase weaponDatabase;
  [SerializeField] private WeaponController weaponController;

  private int medkits;
  private GearLevel helmet = GearLevel.None;
  private GearLevel vest = GearLevel.None;
  private bool hasWeapon;

  public bool HasWeapon => hasWeapon;
  public WeaponController Weapon => weaponController;
  public int Medkits => medkits;

  public bool TryPickupWeapon(WeaponId weaponId)
  {
    if (weaponDatabase == null || weaponController == null)
    {
      return false;
    }

    weaponController.Equip(weaponDatabase.GetStats(weaponId));
    hasWeapon = true;
    return true;
  }

  public void AddMedkit()
  {
    medkits = Mathf.Min(3, medkits + 1);
  }

  public bool TryUseMedkit(BotHealth health)
  {
    if (medkits <= 0 || health == null || !health.IsAlive || health.Health >= 100)
    {
      return false;
    }

    medkits--;
    health.Heal(50);
    return true;
  }

  public void ApplyGear(GearType type, GearLevel level)
  {
    switch (type)
    {
      case GearType.Helmet:
        if (level > helmet) helmet = level;
        break;
      case GearType.Vest:
        if (level > vest) vest = level;
        break;
    }
  }

  public GearLevel Helmet => helmet;
  public GearLevel Vest => vest;
}
