// Generated by the protocol buffer compiler.  DO NOT EDIT!
// source: vma.proto

#ifndef PROTOBUF_vma_2eproto__INCLUDED
#define PROTOBUF_vma_2eproto__INCLUDED

#include <string>

#include <google/protobuf/stubs/common.h>

#if GOOGLE_PROTOBUF_VERSION < 2006000
#error This file was generated by a newer version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please update
#error your headers.
#endif
#if 2006001 < GOOGLE_PROTOBUF_MIN_PROTOC_VERSION
#error This file was generated by an older version of protoc which is
#error incompatible with your Protocol Buffer headers.  Please
#error regenerate this file with a newer version of protoc.
#endif

#include <google/protobuf/generated_message_util.h>
#include <google/protobuf/message.h>
#include <google/protobuf/repeated_field.h>
#include <google/protobuf/extension_set.h>
#include <google/protobuf/unknown_field_set.h>
#include "opts.pb.h"
// @@protoc_insertion_point(includes)

// Internal implementation detail -- do not call these.
void  protobuf_AddDesc_vma_2eproto();
void protobuf_AssignDesc_vma_2eproto();
void protobuf_ShutdownFile_vma_2eproto();

class vma_entry;

// ===================================================================

class vma_entry : public ::google::protobuf::Message {
 public:
  vma_entry();
  virtual ~vma_entry();

  vma_entry(const vma_entry& from);

  inline vma_entry& operator=(const vma_entry& from) {
    CopyFrom(from);
    return *this;
  }

  inline const ::google::protobuf::UnknownFieldSet& unknown_fields() const {
    return _unknown_fields_;
  }

  inline ::google::protobuf::UnknownFieldSet* mutable_unknown_fields() {
    return &_unknown_fields_;
  }

  static const ::google::protobuf::Descriptor* descriptor();
  static const vma_entry& default_instance();

  void Swap(vma_entry* other);

  // implements Message ----------------------------------------------

  vma_entry* New() const;
  void CopyFrom(const ::google::protobuf::Message& from);
  void MergeFrom(const ::google::protobuf::Message& from);
  void CopyFrom(const vma_entry& from);
  void MergeFrom(const vma_entry& from);
  void Clear();
  bool IsInitialized() const;

  int ByteSize() const;
  bool MergePartialFromCodedStream(
      ::google::protobuf::io::CodedInputStream* input);
  void SerializeWithCachedSizes(
      ::google::protobuf::io::CodedOutputStream* output) const;
  ::google::protobuf::uint8* SerializeWithCachedSizesToArray(::google::protobuf::uint8* output) const;
  int GetCachedSize() const { return _cached_size_; }
  private:
  void SharedCtor();
  void SharedDtor();
  void SetCachedSize(int size) const;
  public:
  ::google::protobuf::Metadata GetMetadata() const;

  // nested types ----------------------------------------------------

  // accessors -------------------------------------------------------

  // required uint64 start = 1;
  inline bool has_start() const;
  inline void clear_start();
  static const int kStartFieldNumber = 1;
  inline ::google::protobuf::uint64 start() const;
  inline void set_start(::google::protobuf::uint64 value);

  // required uint64 end = 2;
  inline bool has_end() const;
  inline void clear_end();
  static const int kEndFieldNumber = 2;
  inline ::google::protobuf::uint64 end() const;
  inline void set_end(::google::protobuf::uint64 value);

  // required uint64 pgoff = 3;
  inline bool has_pgoff() const;
  inline void clear_pgoff();
  static const int kPgoffFieldNumber = 3;
  inline ::google::protobuf::uint64 pgoff() const;
  inline void set_pgoff(::google::protobuf::uint64 value);

  // required uint64 shmid = 4;
  inline bool has_shmid() const;
  inline void clear_shmid();
  static const int kShmidFieldNumber = 4;
  inline ::google::protobuf::uint64 shmid() const;
  inline void set_shmid(::google::protobuf::uint64 value);

  // required uint32 prot = 5;
  inline bool has_prot() const;
  inline void clear_prot();
  static const int kProtFieldNumber = 5;
  inline ::google::protobuf::uint32 prot() const;
  inline void set_prot(::google::protobuf::uint32 value);

  // required uint32 flags = 6;
  inline bool has_flags() const;
  inline void clear_flags();
  static const int kFlagsFieldNumber = 6;
  inline ::google::protobuf::uint32 flags() const;
  inline void set_flags(::google::protobuf::uint32 value);

  // required uint32 status = 7;
  inline bool has_status() const;
  inline void clear_status();
  static const int kStatusFieldNumber = 7;
  inline ::google::protobuf::uint32 status() const;
  inline void set_status(::google::protobuf::uint32 value);

  // required sint64 fd = 8;
  inline bool has_fd() const;
  inline void clear_fd();
  static const int kFdFieldNumber = 8;
  inline ::google::protobuf::int64 fd() const;
  inline void set_fd(::google::protobuf::int64 value);

  // optional uint64 madv = 9;
  inline bool has_madv() const;
  inline void clear_madv();
  static const int kMadvFieldNumber = 9;
  inline ::google::protobuf::uint64 madv() const;
  inline void set_madv(::google::protobuf::uint64 value);

  // optional uint32 fdflags = 10;
  inline bool has_fdflags() const;
  inline void clear_fdflags();
  static const int kFdflagsFieldNumber = 10;
  inline ::google::protobuf::uint32 fdflags() const;
  inline void set_fdflags(::google::protobuf::uint32 value);

  // @@protoc_insertion_point(class_scope:vma_entry)
 private:
  inline void set_has_start();
  inline void clear_has_start();
  inline void set_has_end();
  inline void clear_has_end();
  inline void set_has_pgoff();
  inline void clear_has_pgoff();
  inline void set_has_shmid();
  inline void clear_has_shmid();
  inline void set_has_prot();
  inline void clear_has_prot();
  inline void set_has_flags();
  inline void clear_has_flags();
  inline void set_has_status();
  inline void clear_has_status();
  inline void set_has_fd();
  inline void clear_has_fd();
  inline void set_has_madv();
  inline void clear_has_madv();
  inline void set_has_fdflags();
  inline void clear_has_fdflags();

  ::google::protobuf::UnknownFieldSet _unknown_fields_;

  ::google::protobuf::uint32 _has_bits_[1];
  mutable int _cached_size_;
  ::google::protobuf::uint64 start_;
  ::google::protobuf::uint64 end_;
  ::google::protobuf::uint64 pgoff_;
  ::google::protobuf::uint64 shmid_;
  ::google::protobuf::uint32 prot_;
  ::google::protobuf::uint32 flags_;
  ::google::protobuf::int64 fd_;
  ::google::protobuf::uint32 status_;
  ::google::protobuf::uint32 fdflags_;
  ::google::protobuf::uint64 madv_;
  friend void  protobuf_AddDesc_vma_2eproto();
  friend void protobuf_AssignDesc_vma_2eproto();
  friend void protobuf_ShutdownFile_vma_2eproto();

  void InitAsDefaultInstance();
  static vma_entry* default_instance_;
};
// ===================================================================


// ===================================================================

// vma_entry

// required uint64 start = 1;
inline bool vma_entry::has_start() const {
  return (_has_bits_[0] & 0x00000001u) != 0;
}
inline void vma_entry::set_has_start() {
  _has_bits_[0] |= 0x00000001u;
}
inline void vma_entry::clear_has_start() {
  _has_bits_[0] &= ~0x00000001u;
}
inline void vma_entry::clear_start() {
  start_ = GOOGLE_ULONGLONG(0);
  clear_has_start();
}
inline ::google::protobuf::uint64 vma_entry::start() const {
  // @@protoc_insertion_point(field_get:vma_entry.start)
  return start_;
}
inline void vma_entry::set_start(::google::protobuf::uint64 value) {
  set_has_start();
  start_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.start)
}

// required uint64 end = 2;
inline bool vma_entry::has_end() const {
  return (_has_bits_[0] & 0x00000002u) != 0;
}
inline void vma_entry::set_has_end() {
  _has_bits_[0] |= 0x00000002u;
}
inline void vma_entry::clear_has_end() {
  _has_bits_[0] &= ~0x00000002u;
}
inline void vma_entry::clear_end() {
  end_ = GOOGLE_ULONGLONG(0);
  clear_has_end();
}
inline ::google::protobuf::uint64 vma_entry::end() const {
  // @@protoc_insertion_point(field_get:vma_entry.end)
  return end_;
}
inline void vma_entry::set_end(::google::protobuf::uint64 value) {
  set_has_end();
  end_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.end)
}

// required uint64 pgoff = 3;
inline bool vma_entry::has_pgoff() const {
  return (_has_bits_[0] & 0x00000004u) != 0;
}
inline void vma_entry::set_has_pgoff() {
  _has_bits_[0] |= 0x00000004u;
}
inline void vma_entry::clear_has_pgoff() {
  _has_bits_[0] &= ~0x00000004u;
}
inline void vma_entry::clear_pgoff() {
  pgoff_ = GOOGLE_ULONGLONG(0);
  clear_has_pgoff();
}
inline ::google::protobuf::uint64 vma_entry::pgoff() const {
  // @@protoc_insertion_point(field_get:vma_entry.pgoff)
  return pgoff_;
}
inline void vma_entry::set_pgoff(::google::protobuf::uint64 value) {
  set_has_pgoff();
  pgoff_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.pgoff)
}

// required uint64 shmid = 4;
inline bool vma_entry::has_shmid() const {
  return (_has_bits_[0] & 0x00000008u) != 0;
}
inline void vma_entry::set_has_shmid() {
  _has_bits_[0] |= 0x00000008u;
}
inline void vma_entry::clear_has_shmid() {
  _has_bits_[0] &= ~0x00000008u;
}
inline void vma_entry::clear_shmid() {
  shmid_ = GOOGLE_ULONGLONG(0);
  clear_has_shmid();
}
inline ::google::protobuf::uint64 vma_entry::shmid() const {
  // @@protoc_insertion_point(field_get:vma_entry.shmid)
  return shmid_;
}
inline void vma_entry::set_shmid(::google::protobuf::uint64 value) {
  set_has_shmid();
  shmid_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.shmid)
}

// required uint32 prot = 5;
inline bool vma_entry::has_prot() const {
  return (_has_bits_[0] & 0x00000010u) != 0;
}
inline void vma_entry::set_has_prot() {
  _has_bits_[0] |= 0x00000010u;
}
inline void vma_entry::clear_has_prot() {
  _has_bits_[0] &= ~0x00000010u;
}
inline void vma_entry::clear_prot() {
  prot_ = 0u;
  clear_has_prot();
}
inline ::google::protobuf::uint32 vma_entry::prot() const {
  // @@protoc_insertion_point(field_get:vma_entry.prot)
  return prot_;
}
inline void vma_entry::set_prot(::google::protobuf::uint32 value) {
  set_has_prot();
  prot_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.prot)
}

// required uint32 flags = 6;
inline bool vma_entry::has_flags() const {
  return (_has_bits_[0] & 0x00000020u) != 0;
}
inline void vma_entry::set_has_flags() {
  _has_bits_[0] |= 0x00000020u;
}
inline void vma_entry::clear_has_flags() {
  _has_bits_[0] &= ~0x00000020u;
}
inline void vma_entry::clear_flags() {
  flags_ = 0u;
  clear_has_flags();
}
inline ::google::protobuf::uint32 vma_entry::flags() const {
  // @@protoc_insertion_point(field_get:vma_entry.flags)
  return flags_;
}
inline void vma_entry::set_flags(::google::protobuf::uint32 value) {
  set_has_flags();
  flags_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.flags)
}

// required uint32 status = 7;
inline bool vma_entry::has_status() const {
  return (_has_bits_[0] & 0x00000040u) != 0;
}
inline void vma_entry::set_has_status() {
  _has_bits_[0] |= 0x00000040u;
}
inline void vma_entry::clear_has_status() {
  _has_bits_[0] &= ~0x00000040u;
}
inline void vma_entry::clear_status() {
  status_ = 0u;
  clear_has_status();
}
inline ::google::protobuf::uint32 vma_entry::status() const {
  // @@protoc_insertion_point(field_get:vma_entry.status)
  return status_;
}
inline void vma_entry::set_status(::google::protobuf::uint32 value) {
  set_has_status();
  status_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.status)
}

// required sint64 fd = 8;
inline bool vma_entry::has_fd() const {
  return (_has_bits_[0] & 0x00000080u) != 0;
}
inline void vma_entry::set_has_fd() {
  _has_bits_[0] |= 0x00000080u;
}
inline void vma_entry::clear_has_fd() {
  _has_bits_[0] &= ~0x00000080u;
}
inline void vma_entry::clear_fd() {
  fd_ = GOOGLE_LONGLONG(0);
  clear_has_fd();
}
inline ::google::protobuf::int64 vma_entry::fd() const {
  // @@protoc_insertion_point(field_get:vma_entry.fd)
  return fd_;
}
inline void vma_entry::set_fd(::google::protobuf::int64 value) {
  set_has_fd();
  fd_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.fd)
}

// optional uint64 madv = 9;
inline bool vma_entry::has_madv() const {
  return (_has_bits_[0] & 0x00000100u) != 0;
}
inline void vma_entry::set_has_madv() {
  _has_bits_[0] |= 0x00000100u;
}
inline void vma_entry::clear_has_madv() {
  _has_bits_[0] &= ~0x00000100u;
}
inline void vma_entry::clear_madv() {
  madv_ = GOOGLE_ULONGLONG(0);
  clear_has_madv();
}
inline ::google::protobuf::uint64 vma_entry::madv() const {
  // @@protoc_insertion_point(field_get:vma_entry.madv)
  return madv_;
}
inline void vma_entry::set_madv(::google::protobuf::uint64 value) {
  set_has_madv();
  madv_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.madv)
}

// optional uint32 fdflags = 10;
inline bool vma_entry::has_fdflags() const {
  return (_has_bits_[0] & 0x00000200u) != 0;
}
inline void vma_entry::set_has_fdflags() {
  _has_bits_[0] |= 0x00000200u;
}
inline void vma_entry::clear_has_fdflags() {
  _has_bits_[0] &= ~0x00000200u;
}
inline void vma_entry::clear_fdflags() {
  fdflags_ = 0u;
  clear_has_fdflags();
}
inline ::google::protobuf::uint32 vma_entry::fdflags() const {
  // @@protoc_insertion_point(field_get:vma_entry.fdflags)
  return fdflags_;
}
inline void vma_entry::set_fdflags(::google::protobuf::uint32 value) {
  set_has_fdflags();
  fdflags_ = value;
  // @@protoc_insertion_point(field_set:vma_entry.fdflags)
}


// @@protoc_insertion_point(namespace_scope)

#ifndef SWIG
namespace google {
namespace protobuf {


}  // namespace google
}  // namespace protobuf
#endif  // SWIG

// @@protoc_insertion_point(global_scope)

#endif  // PROTOBUF_vma_2eproto__INCLUDED
