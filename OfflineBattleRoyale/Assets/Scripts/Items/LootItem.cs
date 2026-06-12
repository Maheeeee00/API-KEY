using UnityEngine;

public abstract class LootItem : MonoBehaviour
{
  [SerializeField] private float rotationSpeed = 90f;
  [SerializeField] private float bobAmplitude = 0.15f;
  [SerializeField] private float bobSpeed = 2f;

  private Vector3 startPosition;
  private bool collected;

  private void Start()
  {
    startPosition = transform.position;
  }

  private void Update()
  {
    if (collected)
    {
      return;
    }

    transform.Rotate(Vector3.up, rotationSpeed * Time.deltaTime, Space.World);
    float bob = Mathf.Sin(Time.time * bobSpeed) * bobAmplitude;
    transform.position = startPosition + Vector3.up * bob;
  }

  private void OnTriggerEnter(Collider other)
  {
    if (collected)
    {
      return;
    }

    if (TryCollect(other.gameObject))
    {
      collected = true;
      Destroy(gameObject);
    }
  }

  protected abstract bool TryCollect(GameObject collector);
}
