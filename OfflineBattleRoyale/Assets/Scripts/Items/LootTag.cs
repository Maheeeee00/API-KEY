using UnityEngine;

[RequireComponent(typeof(Collider))]
public class LootTag : MonoBehaviour
{
  private void Awake()
  {
    gameObject.tag = "Loot";
    Collider collider = GetComponent<Collider>();
    collider.isTrigger = true;
  }
}
